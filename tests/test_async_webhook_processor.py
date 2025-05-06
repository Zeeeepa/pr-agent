"""
Test script for the asynchronous webhook processor.
"""

import asyncio
import json
import os
import time
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from pr_agent.servers.async_webhook_processor import (
    WebhookProcessor, WebhookQueue, WebhookStatus, WebhookTask,
    get_webhook_processor, start_webhook_processor, stop_webhook_processor
)


class TestWebhookTask(unittest.TestCase):
    """Test the WebhookTask class."""
    
    def test_init(self):
        """Test initialization of a webhook task."""
        task = WebhookTask("test-id", "github", "push", {"key": "value"})
        self.assertEqual(task.webhook_id, "test-id")
        self.assertEqual(task.source, "github")
        self.assertEqual(task.event_type, "push")
        self.assertEqual(task.payload, {"key": "value"})
        self.assertEqual(task.status, WebhookStatus.QUEUED)
        self.assertEqual(task.attempts, 0)
        self.assertIsNone(task.error)
        self.assertIsNone(task.result)
    
    def test_to_dict(self):
        """Test conversion of a webhook task to a dictionary."""
        task = WebhookTask("test-id", "github", "push", {"key": "value"})
        task_dict = task.to_dict()
        self.assertEqual(task_dict["webhook_id"], "test-id")
        self.assertEqual(task_dict["source"], "github")
        self.assertEqual(task_dict["event_type"], "push")
        self.assertEqual(task_dict["payload"], {"key": "value"})
        self.assertEqual(task_dict["status"], "queued")
        self.assertEqual(task_dict["attempts"], 0)
        self.assertIsNone(task_dict["error"])
        self.assertIsNone(task_dict["result"])
    
    def test_from_dict(self):
        """Test creation of a webhook task from a dictionary."""
        task_dict = {
            "webhook_id": "test-id",
            "source": "github",
            "event_type": "push",
            "payload": {"key": "value"},
            "status": "processing",
            "created_at": 1620000000.0,
            "updated_at": 1620000001.0,
            "attempts": 1,
            "max_attempts": 3,
            "error": None,
            "result": {"status": "success"}
        }
        task = WebhookTask.from_dict(task_dict)
        self.assertEqual(task.webhook_id, "test-id")
        self.assertEqual(task.source, "github")
        self.assertEqual(task.event_type, "push")
        self.assertEqual(task.payload, {"key": "value"})
        self.assertEqual(task.status, WebhookStatus.PROCESSING)
        self.assertEqual(task.created_at, 1620000000.0)
        self.assertEqual(task.updated_at, 1620000001.0)
        self.assertEqual(task.attempts, 1)
        self.assertEqual(task.max_attempts, 3)
        self.assertIsNone(task.error)
        self.assertEqual(task.result, {"status": "success"})
    
    def test_update_status(self):
        """Test updating the status of a webhook task."""
        task = WebhookTask("test-id", "github", "push", {"key": "value"})
        original_updated_at = task.updated_at
        time.sleep(0.001)  # Ensure updated_at changes
        task.update_status(WebhookStatus.PROCESSING)
        self.assertEqual(task.status, WebhookStatus.PROCESSING)
        self.assertGreater(task.updated_at, original_updated_at)
        
        # Test with error
        error = Exception("Test error")
        task.update_status(WebhookStatus.FAILED, error=error)
        self.assertEqual(task.status, WebhookStatus.FAILED)
        self.assertEqual(task.error, error)
    
    def test_should_retry(self):
        """Test checking if a task should be retried."""
        task = WebhookTask("test-id", "github", "push", {"key": "value"})
        
        # Not failed, should not retry
        self.assertFalse(task.should_retry())
        
        # Failed but no attempts yet, should retry
        task.update_status(WebhookStatus.FAILED)
        self.assertTrue(task.should_retry())
        
        # Failed with max attempts reached, should not retry
        task.attempts = task.max_attempts
        self.assertFalse(task.should_retry())


@pytest.mark.asyncio
class TestWebhookQueue:
    """Test the WebhookQueue class."""
    
    @pytest.fixture
    async def queue(self):
        """Create a webhook queue for testing."""
        return WebhookQueue()
    
    async def test_enqueue_dequeue(self, queue):
        """Test enqueueing and dequeueing a webhook task."""
        task = WebhookTask("test-id", "github", "push", {"key": "value"})
        
        # Enqueue
        webhook_id = await queue.enqueue(task)
        assert webhook_id == "test-id"
        
        # Dequeue
        dequeued_task = await queue.dequeue()
        assert dequeued_task.webhook_id == "test-id"
        assert dequeued_task.status == WebhookStatus.PROCESSING
        assert dequeued_task.attempts == 1
    
    async def test_get_task(self, queue):
        """Test getting a webhook task by ID."""
        task = WebhookTask("test-id", "github", "push", {"key": "value"})
        await queue.enqueue(task)
        
        # Get task
        retrieved_task = await queue.get_task("test-id")
        assert retrieved_task.webhook_id == "test-id"
        
        # Get non-existent task
        non_existent_task = await queue.get_task("non-existent-id")
        assert non_existent_task is None
    
    async def test_update_task(self, queue):
        """Test updating a webhook task."""
        task = WebhookTask("test-id", "github", "push", {"key": "value"})
        await queue.enqueue(task)
        
        # Update task
        task.update_status(WebhookStatus.COMPLETED)
        await queue.update_task(task)
        
        # Verify update
        updated_task = await queue.get_task("test-id")
        assert updated_task.status == WebhookStatus.COMPLETED
    
    async def test_requeue(self, queue):
        """Test requeuing a failed webhook task."""
        task = WebhookTask("test-id", "github", "push", {"key": "value"})
        task.update_status(WebhookStatus.FAILED)
        await queue.enqueue(task)
        
        # Dequeue and requeue
        dequeued_task = await queue.dequeue()
        await queue.requeue(dequeued_task)
        
        # Verify requeue
        requeued_task = await queue.dequeue()
        assert requeued_task.webhook_id == "test-id"
        assert requeued_task.status == WebhookStatus.PROCESSING
        assert requeued_task.attempts == 2
    
    async def test_get_all_tasks(self, queue):
        """Test getting all webhook tasks."""
        task1 = WebhookTask("test-id-1", "github", "push", {"key": "value1"})
        task2 = WebhookTask("test-id-2", "github", "push", {"key": "value2"})
        await queue.enqueue(task1)
        await queue.enqueue(task2)
        
        # Get all tasks
        all_tasks = await queue.get_all_tasks()
        assert len(all_tasks) == 2
        assert {task.webhook_id for task in all_tasks} == {"test-id-1", "test-id-2"}
    
    async def test_cleanup_old_tasks(self, queue):
        """Test cleaning up old webhook tasks."""
        # Create tasks with different timestamps
        task1 = WebhookTask("test-id-1", "github", "push", {"key": "value1"})
        task1.update_status(WebhookStatus.COMPLETED)
        task1.updated_at = time.time() - 100  # 100 seconds old
        
        task2 = WebhookTask("test-id-2", "github", "push", {"key": "value2"})
        task2.update_status(WebhookStatus.FAILED)
        task2.updated_at = time.time() - 200  # 200 seconds old
        
        task3 = WebhookTask("test-id-3", "github", "push", {"key": "value3"})
        task3.update_status(WebhookStatus.PROCESSING)
        task3.updated_at = time.time() - 300  # 300 seconds old
        
        # Add tasks to queue
        await queue.enqueue(task1)
        await queue.enqueue(task2)
        await queue.enqueue(task3)
        
        # Clean up tasks older than 150 seconds
        removed_count = await queue.cleanup_old_tasks(max_age_seconds=150)
        
        # Verify cleanup
        assert removed_count == 1  # Only task2 should be removed (task3 is not completed/failed)
        all_tasks = await queue.get_all_tasks()
        assert len(all_tasks) == 2
        assert {task.webhook_id for task in all_tasks} == {"test-id-1", "test-id-3"}


@pytest.mark.asyncio
class TestWebhookProcessor:
    """Test the WebhookProcessor class."""
    
    @pytest.fixture
    async def processor(self):
        """Create a webhook processor for testing."""
        processor = WebhookProcessor(num_workers=2)
        processor.enable_persistence = False  # Disable persistence for testing
        return processor
    
    async def test_register_handler(self, processor):
        """Test registering a handler function."""
        handler = AsyncMock()
        processor.register_handler("github", "push", handler)
        assert ("github", "push") in processor.handlers
        assert processor.handlers[("github", "push")] == handler
    
    async def test_process_webhook_success(self, processor):
        """Test processing a webhook task successfully."""
        # Register handler
        handler = AsyncMock(return_value={"status": "success"})
        processor.register_handler("github", "push", handler)
        
        # Create task
        task = WebhookTask("test-id", "github", "push", {"key": "value"})
        
        # Process webhook
        await processor.process_webhook(task)
        
        # Verify processing
        handler.assert_called_once_with({"key": "value"})
        assert task.status == WebhookStatus.COMPLETED
        assert task.result == {"status": "success"}
    
    async def test_process_webhook_failure(self, processor):
        """Test processing a webhook task with failure."""
        # Register handler that raises an exception
        error = Exception("Test error")
        handler = AsyncMock(side_effect=error)
        processor.register_handler("github", "push", handler)
        
        # Create task
        task = WebhookTask("test-id", "github", "push", {"key": "value"})
        
        # Mock requeue method
        processor.queue.requeue = AsyncMock()
        
        # Process webhook
        await processor.process_webhook(task)
        
        # Verify processing
        handler.assert_called_once_with({"key": "value"})
        assert task.status == WebhookStatus.FAILED
        assert task.error == error
        processor.queue.requeue.assert_called_once_with(task)
    
    async def test_process_webhook_no_handler(self, processor):
        """Test processing a webhook task with no handler."""
        # Create task with no registered handler
        task = WebhookTask("test-id", "github", "push", {"key": "value"})
        
        # Process webhook
        await processor.process_webhook(task)
        
        # Verify processing
        assert task.status == WebhookStatus.FAILED
        assert isinstance(task.error, ValueError)
        assert "No handler registered" in str(task.error)
    
    async def test_process_webhook_wildcard_handler(self, processor):
        """Test processing a webhook task with a wildcard handler."""
        # Register wildcard handler
        handler = AsyncMock(return_value={"status": "success"})
        processor.register_handler("github", "*", handler)
        
        # Create task
        task = WebhookTask("test-id", "github", "push", {"key": "value"})
        
        # Process webhook
        await processor.process_webhook(task)
        
        # Verify processing
        handler.assert_called_once_with({"key": "value"})
        assert task.status == WebhookStatus.COMPLETED
        assert task.result == {"status": "success"}
    
    async def test_start_stop(self, processor):
        """Test starting and stopping the webhook processor."""
        # Start processor
        await processor.start()
        assert processor.running
        assert len(processor.worker_tasks) == 2
        
        # Stop processor
        await processor.stop()
        assert not processor.running
        assert len(processor.worker_tasks) == 0
    
    async def test_enqueue_webhook(self, processor):
        """Test enqueueing a webhook."""
        # Mock queue.enqueue method
        processor.queue.enqueue = AsyncMock(return_value="test-id")
        
        # Enqueue webhook
        webhook_id = await processor.enqueue_webhook("github", "push", {"key": "value"})
        
        # Verify enqueueing
        assert webhook_id == "test-id"
        processor.queue.enqueue.assert_called_once()
        task = processor.queue.enqueue.call_args[0][0]
        assert task.source == "github"
        assert task.event_type == "push"
        assert task.payload == {"key": "value"}
    
    async def test_get_webhook_status(self, processor):
        """Test getting the status of a webhook task."""
        # Create task
        task = WebhookTask("test-id", "github", "push", {"key": "value"})
        task.update_status(WebhookStatus.PROCESSING)
        
        # Mock queue.get_task method
        processor.queue.get_task = AsyncMock(return_value=task)
        
        # Get webhook status
        status = await processor.get_webhook_status("test-id")
        
        # Verify status
        assert status["webhook_id"] == "test-id"
        assert status["status"] == "processing"
        assert status["source"] == "github"
        assert status["event_type"] == "push"
    
    async def test_get_all_webhook_statuses(self, processor):
        """Test getting the status of all webhook tasks."""
        # Create tasks
        task1 = WebhookTask("test-id-1", "github", "push", {"key": "value1"})
        task1.update_status(WebhookStatus.PROCESSING)
        task2 = WebhookTask("test-id-2", "github", "push", {"key": "value2"})
        task2.update_status(WebhookStatus.COMPLETED)
        
        # Mock queue.get_all_tasks method
        processor.queue.get_all_tasks = AsyncMock(return_value=[task1, task2])
        
        # Get all webhook statuses
        statuses = await processor.get_all_webhook_statuses()
        
        # Verify statuses
        assert len(statuses) == 2
        assert {status["webhook_id"] for status in statuses} == {"test-id-1", "test-id-2"}
        assert {status["status"] for status in statuses} == {"processing", "completed"}
    
    async def test_cleanup(self, processor):
        """Test cleaning up old webhook tasks."""
        # Mock queue.cleanup_old_tasks method
        processor.queue.cleanup_old_tasks = AsyncMock(return_value=3)
        
        # Clean up tasks
        removed_count = await processor.cleanup()
        
        # Verify cleanup
        assert removed_count == 3
        processor.queue.cleanup_old_tasks.assert_called_once_with(86400)  # Default max age


@pytest.mark.asyncio
class TestGlobalWebhookProcessor:
    """Test the global webhook processor functions."""
    
    async def test_get_webhook_processor(self):
        """Test getting the global webhook processor instance."""
        # Reset global processor
        from pr_agent.servers.async_webhook_processor import _webhook_processor
        _webhook_processor = None
        
        # Get processor
        processor1 = get_webhook_processor()
        processor2 = get_webhook_processor()
        
        # Verify singleton behavior
        assert processor1 is processor2
        assert processor1.num_workers == 5  # Default value
    
    async def test_start_stop_webhook_processor(self):
        """Test starting and stopping the global webhook processor."""
        # Reset global processor
        from pr_agent.servers.async_webhook_processor import _webhook_processor
        _webhook_processor = None
        
        # Mock WebhookProcessor.start and stop methods
        with patch("pr_agent.servers.async_webhook_processor.WebhookProcessor.start", new_callable=AsyncMock) as mock_start, \
             patch("pr_agent.servers.async_webhook_processor.WebhookProcessor.stop", new_callable=AsyncMock) as mock_stop:
            
            # Start processor
            await start_webhook_processor()
            mock_start.assert_called_once()
            
            # Stop processor
            await stop_webhook_processor()
            mock_stop.assert_called_once()
            
            # Verify global processor is reset
            from pr_agent.servers.async_webhook_processor import _webhook_processor
            assert _webhook_processor is None


if __name__ == "__main__":
    unittest.main()

