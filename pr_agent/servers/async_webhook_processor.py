"""
Asynchronous Webhook Processing Module

This module provides functionality for asynchronous processing of webhooks,
including:
- Quick response to webhook sources to prevent timeouts
- Background processing of webhook events
- Status tracking for webhook processing
- Error handling and retry mechanisms
- Isolation between concurrent webhook processing tasks
"""

import asyncio
import json
import time
import uuid
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple
from pathlib import Path

from pr_agent.log import get_logger
from pr_agent.config_loader import get_settings
from pr_agent.servers.utils import DefaultDictWithTimeout


class WebhookStatus(Enum):
    """Status of a webhook processing task."""
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"


class WebhookTask:
    """Represents a webhook processing task."""
    
    def __init__(self, webhook_id: str, source: str, event_type: str, payload: Dict[str, Any]):
        """
        Initialize a webhook task.
        
        Args:
            webhook_id: Unique identifier for the webhook
            source: Source of the webhook (github, gitlab, etc.)
            event_type: Type of the webhook event
            payload: Webhook payload data
        """
        self.webhook_id = webhook_id
        self.source = source
        self.event_type = event_type
        self.payload = payload
        self.status = WebhookStatus.QUEUED
        self.created_at = time.time()
        self.updated_at = time.time()
        self.attempts = 0
        self.max_attempts = get_settings().get("WEBHOOK_PROCESSOR.MAX_RETRY_ATTEMPTS", 3)
        self.error = None
        self.result = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the webhook task to a dictionary for serialization."""
        return {
            "webhook_id": self.webhook_id,
            "source": self.source,
            "event_type": self.event_type,
            "payload": self.payload,
            "status": self.status.value,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "attempts": self.attempts,
            "max_attempts": self.max_attempts,
            "error": str(self.error) if self.error else None,
            "result": self.result
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WebhookTask':
        """Create a webhook task from a dictionary."""
        task = cls(
            webhook_id=data["webhook_id"],
            source=data["source"],
            event_type=data["event_type"],
            payload=data["payload"]
        )
        task.status = WebhookStatus(data["status"])
        task.created_at = data["created_at"]
        task.updated_at = data["updated_at"]
        task.attempts = data["attempts"]
        task.max_attempts = data["max_attempts"]
        task.error = data["error"]
        task.result = data["result"]
        return task
    
    def update_status(self, status: WebhookStatus, error: Optional[Exception] = None) -> None:
        """
        Update the status of the webhook task.
        
        Args:
            status: New status
            error: Optional error if the task failed
        """
        self.status = status
        self.updated_at = time.time()
        if error:
            self.error = error
    
    def should_retry(self) -> bool:
        """Check if the task should be retried."""
        return (
            self.status == WebhookStatus.FAILED and 
            self.attempts < self.max_attempts
        )


class WebhookQueue:
    """Queue for webhook processing tasks."""
    
    def __init__(self):
        """Initialize the webhook queue."""
        self.queue = asyncio.Queue()
        self.tasks = {}  # webhook_id -> WebhookTask
        self.lock = asyncio.Lock()
    
    async def enqueue(self, task: WebhookTask) -> str:
        """
        Add a webhook task to the queue.
        
        Args:
            task: Webhook task to enqueue
            
        Returns:
            Webhook ID
        """
        async with self.lock:
            self.tasks[task.webhook_id] = task
        await self.queue.put(task.webhook_id)
        get_logger().info(
            f"Enqueued webhook task {task.webhook_id} from {task.source} of type {task.event_type}"
        )
        return task.webhook_id
    
    async def dequeue(self) -> Optional[WebhookTask]:
        """
        Get the next webhook task from the queue.
        
        Returns:
            Next webhook task or None if the queue is empty
        """
        try:
            webhook_id = await self.queue.get()
            async with self.lock:
                task = self.tasks.get(webhook_id)
                if task:
                    task.update_status(WebhookStatus.PROCESSING)
                    task.attempts += 1
            return task
        except asyncio.QueueEmpty:
            return None
    
    async def get_task(self, webhook_id: str) -> Optional[WebhookTask]:
        """
        Get a webhook task by ID.
        
        Args:
            webhook_id: Webhook task ID
            
        Returns:
            Webhook task or None if not found
        """
        async with self.lock:
            return self.tasks.get(webhook_id)
    
    async def update_task(self, task: WebhookTask) -> None:
        """
        Update a webhook task in the queue.
        
        Args:
            task: Updated webhook task
        """
        async with self.lock:
            self.tasks[task.webhook_id] = task
    
    async def requeue(self, task: WebhookTask) -> None:
        """
        Requeue a failed webhook task for retry.
        
        Args:
            task: Failed webhook task
        """
        if task.should_retry():
            task.update_status(WebhookStatus.RETRYING)
            await self.queue.put(task.webhook_id)
            get_logger().info(
                f"Requeued webhook task {task.webhook_id} for retry (attempt {task.attempts + 1}/{task.max_attempts})"
            )
    
    async def get_all_tasks(self) -> List[WebhookTask]:
        """
        Get all webhook tasks.
        
        Returns:
            List of all webhook tasks
        """
        async with self.lock:
            return list(self.tasks.values())
    
    async def cleanup_old_tasks(self, max_age_seconds: int = 86400) -> int:
        """
        Remove old completed or failed tasks.
        
        Args:
            max_age_seconds: Maximum age of tasks to keep (default: 24 hours)
            
        Returns:
            Number of tasks removed
        """
        now = time.time()
        to_remove = []
        
        async with self.lock:
            for webhook_id, task in self.tasks.items():
                if (task.status in (WebhookStatus.COMPLETED, WebhookStatus.FAILED) and
                        now - task.updated_at > max_age_seconds):
                    to_remove.append(webhook_id)
            
            for webhook_id in to_remove:
                del self.tasks[webhook_id]
        
        return len(to_remove)


class WebhookProcessor:
    """Processor for webhook tasks."""
    
    def __init__(self, num_workers: int = 5):
        """
        Initialize the webhook processor.
        
        Args:
            num_workers: Number of worker tasks to run concurrently
        """
        self.queue = WebhookQueue()
        self.num_workers = num_workers
        self.worker_tasks = []
        self.running = False
        self.handlers = {}  # (source, event_type) -> handler_function
        
        # Persistence settings
        self.enable_persistence = get_settings().get("WEBHOOK_PROCESSOR.ENABLE_PERSISTENCE", False)
        self.persistence_file = get_settings().get("WEBHOOK_PROCESSOR.PERSISTENCE_FILE", "data/webhook_tasks.json")
        self.persistence_interval = get_settings().get("WEBHOOK_PROCESSOR.PERSISTENCE_INTERVAL", 300)
        self.persistence_task = None
    
    def register_handler(self, source: str, event_type: str, handler: Callable) -> None:
        """
        Register a handler function for a specific webhook source and event type.
        
        Args:
            source: Webhook source (github, gitlab, etc.)
            event_type: Webhook event type
            handler: Handler function that takes a webhook payload and returns a result
        """
        self.handlers[(source, event_type)] = handler
        get_logger().info(f"Registered handler for {source} {event_type} webhooks")
    
    async def process_webhook(self, task: WebhookTask) -> None:
        """
        Process a webhook task.
        
        Args:
            task: Webhook task to process
        """
        try:
            handler = self.handlers.get((task.source, task.event_type))
            if not handler:
                handler = self.handlers.get((task.source, "*"))  # Fallback to wildcard handler
            
            if not handler:
                raise ValueError(f"No handler registered for {task.source} {task.event_type} webhooks")
            
            get_logger().info(
                f"Processing webhook task {task.webhook_id} from {task.source} of type {task.event_type}"
            )
            
            result = await handler(task.payload)
            task.result = result
            task.update_status(WebhookStatus.COMPLETED)
            
            get_logger().info(
                f"Completed webhook task {task.webhook_id} from {task.source} of type {task.event_type}"
            )
        except Exception as e:
            get_logger().error(
                f"Failed to process webhook task {task.webhook_id}: {str(e)}",
                exc_info=True
            )
            task.update_status(WebhookStatus.FAILED, error=e)
            
            if task.should_retry():
                await self.queue.requeue(task)
            else:
                get_logger().error(
                    f"Webhook task {task.webhook_id} failed after {task.attempts} attempts"
                )
        finally:
            await self.queue.update_task(task)
    
    async def worker(self, worker_id: int) -> None:
        """
        Worker task that processes webhooks from the queue.
        
        Args:
            worker_id: Worker identifier
        """
        get_logger().info(f"Starting webhook worker {worker_id}")
        
        while self.running:
            try:
                task = await self.queue.dequeue()
                if task:
                    await self.process_webhook(task)
            except Exception as e:
                get_logger().error(f"Error in webhook worker {worker_id}: {str(e)}", exc_info=True)
                await asyncio.sleep(1)  # Prevent tight loop on persistent errors
        
        get_logger().info(f"Stopping webhook worker {worker_id}")
    
    async def start(self) -> None:
        """Start the webhook processor."""
        if self.running:
            return
        
        self.running = True
        
        # Load persisted tasks if enabled
        if self.enable_persistence:
            await self._load_persisted_tasks()
            
            # Start persistence task
            self.persistence_task = asyncio.create_task(self._persistence_loop())
        
        self.worker_tasks = [
            asyncio.create_task(self.worker(i))
            for i in range(self.num_workers)
        ]
        
        get_logger().info(f"Started webhook processor with {self.num_workers} workers")
    
    async def stop(self) -> None:
        """Stop the webhook processor."""
        if not self.running:
            return
        
        self.running = False
        
        # Persist tasks before stopping if enabled
        if self.enable_persistence:
            await self._persist_tasks()
            
            # Cancel persistence task
            if self.persistence_task:
                self.persistence_task.cancel()
                try:
                    await self.persistence_task
                except asyncio.CancelledError:
                    pass
        
        # Wait for all worker tasks to complete
        if self.worker_tasks:
            await asyncio.gather(*self.worker_tasks, return_exceptions=True)
            self.worker_tasks = []
        
        get_logger().info("Stopped webhook processor")
    
    async def _persistence_loop(self) -> None:
        """Periodically persist webhook tasks to disk."""
        try:
            while self.running:
                await asyncio.sleep(self.persistence_interval)
                await self._persist_tasks()
        except asyncio.CancelledError:
            # Final persistence before exiting
            await self._persist_tasks()
            raise
    
    async def _persist_tasks(self) -> None:
        """Persist webhook tasks to disk."""
        if not self.enable_persistence:
            return
        
        try:
            tasks = await self.queue.get_all_tasks()
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self.persistence_file), exist_ok=True)
            
            # Serialize tasks
            serialized_tasks = [task.to_dict() for task in tasks]
            
            # Write to temporary file first to avoid corruption
            temp_file = f"{self.persistence_file}.tmp"
            with open(temp_file, "w") as f:
                json.dump(serialized_tasks, f)
            
            # Rename to actual file (atomic operation)
            os.replace(temp_file, self.persistence_file)
            
            get_logger().info(f"Persisted {len(tasks)} webhook tasks to {self.persistence_file}")
        except Exception as e:
            get_logger().error(f"Failed to persist webhook tasks: {str(e)}", exc_info=True)
    
    async def _load_persisted_tasks(self) -> None:
        """Load persisted webhook tasks from disk."""
        if not self.enable_persistence or not os.path.exists(self.persistence_file):
            return
        
        try:
            with open(self.persistence_file, "r") as f:
                serialized_tasks = json.load(f)
            
            # Deserialize tasks
            for task_dict in serialized_tasks:
                task = WebhookTask.from_dict(task_dict)
                
                # Only requeue tasks that are still in progress
                if task.status in (WebhookStatus.QUEUED, WebhookStatus.PROCESSING, WebhookStatus.RETRYING):
                    await self.queue.enqueue(task)
                else:
                    # Just add completed/failed tasks to the registry
                    async with self.queue.lock:
                        self.queue.tasks[task.webhook_id] = task
            
            get_logger().info(f"Loaded {len(serialized_tasks)} webhook tasks from {self.persistence_file}")
        except Exception as e:
            get_logger().error(f"Failed to load persisted webhook tasks: {str(e)}", exc_info=True)
    
    async def enqueue_webhook(
        self, source: str, event_type: str, payload: Dict[str, Any]
    ) -> str:
        """
        Enqueue a webhook for processing.
        
        Args:
            source: Webhook source (github, gitlab, etc.)
            event_type: Webhook event type
            payload: Webhook payload data
            
        Returns:
            Webhook ID
        """
        webhook_id = str(uuid.uuid4())
        task = WebhookTask(webhook_id, source, event_type, payload)
        return await self.queue.enqueue(task)
    
    async def get_webhook_status(self, webhook_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the status of a webhook task.
        
        Args:
            webhook_id: Webhook task ID
            
        Returns:
            Webhook task status or None if not found
        """
        task = await self.queue.get_task(webhook_id)
        if task:
            return {
                "webhook_id": task.webhook_id,
                "status": task.status.value,
                "created_at": task.created_at,
                "updated_at": task.updated_at,
                "attempts": task.attempts,
                "source": task.source,
                "event_type": task.event_type,
                "error": str(task.error) if task.error else None
            }
        return None
    
    async def get_all_webhook_statuses(self) -> List[Dict[str, Any]]:
        """
        Get the status of all webhook tasks.
        
        Returns:
            List of webhook task statuses
        """
        tasks = await self.queue.get_all_tasks()
        return [
            {
                "webhook_id": task.webhook_id,
                "status": task.status.value,
                "created_at": task.created_at,
                "updated_at": task.updated_at,
                "attempts": task.attempts,
                "source": task.source,
                "event_type": task.event_type,
                "error": str(task.error) if task.error else None
            }
            for task in tasks
        ]
    
    async def cleanup(self) -> int:
        """
        Clean up old webhook tasks.
        
        Returns:
            Number of tasks removed
        """
        max_age_seconds = get_settings().get("WEBHOOK_PROCESSOR.CLEANUP_AGE", 86400)
        return await self.queue.cleanup_old_tasks(max_age_seconds)


# Global webhook processor instance
_webhook_processor = None


def get_webhook_processor() -> WebhookProcessor:
    """
    Get the global webhook processor instance.
    
    Returns:
        Global webhook processor instance
    """
    global _webhook_processor
    if _webhook_processor is None:
        num_workers = get_settings().get("WEBHOOK_PROCESSOR.NUM_WORKERS", 5)
        _webhook_processor = WebhookProcessor(num_workers=num_workers)
    return _webhook_processor


async def start_webhook_processor() -> None:
    """Start the global webhook processor."""
    processor = get_webhook_processor()
    await processor.start()


async def stop_webhook_processor() -> None:
    """Stop the global webhook processor."""
    global _webhook_processor
    if _webhook_processor:
        await _webhook_processor.stop()
        _webhook_processor = None
