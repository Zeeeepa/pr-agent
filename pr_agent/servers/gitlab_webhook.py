import copy
import json
import re
from datetime import datetime

import uvicorn
from fastapi import APIRouter, FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from starlette.background import BackgroundTasks
from starlette.middleware import Middleware
from starlette_context import context
from starlette_context.middleware import RawContextMiddleware

from pr_agent.agent.pr_agent import PRAgent
from pr_agent.algo.utils import update_settings_from_args
from pr_agent.config_loader import get_settings, global_settings
from pr_agent.git_providers.utils import apply_repo_settings
from pr_agent.log import LoggingFormat, get_logger, setup_logger
from pr_agent.secret_providers import get_secret_provider
from pr_agent.servers.async_webhook_processor import get_webhook_processor, start_webhook_processor, WebhookStatus

setup_logger(fmt=LoggingFormat.JSON, level=get_settings().get("CONFIG.LOG_LEVEL", "DEBUG"))
router = APIRouter()

secret_provider = get_secret_provider() if get_settings().get("CONFIG.SECRET_PROVIDER") else None

# Initialize the webhook processor on startup
@router.on_event("startup")
async def startup_event():
    await start_webhook_processor()
    
    # Register handlers for GitLab webhooks
    webhook_processor = get_webhook_processor()
    
    # Register handler for merge request events
    webhook_processor.register_handler("gitlab", "merge_request", gitlab_merge_request_handler)
    
    # Register handler for note (comment) events
    webhook_processor.register_handler("gitlab", "note", gitlab_note_handler)
    
    # Register fallback handler for other GitLab events
    webhook_processor.register_handler("gitlab", "*", gitlab_fallback_handler)


# Webhook handlers for asynchronous processing
async def gitlab_merge_request_handler(payload: dict) -> dict:
    """Handler for GitLab merge request events."""
    if not payload.get('object_attributes', {}):
        return {"status": "ignored", "reason": "missing_object_attributes"}
    
    # Check if we should process this MR
    if not should_process_pr_logic(payload):
        return {"status": "ignored", "reason": "pr_logic_filtering"}
    
    # Check if it's a bot user
    if is_bot_user(payload):
        return {"status": "ignored", "reason": "bot_user"}
    
    object_attributes = payload.get('object_attributes', {})
    action = object_attributes.get('action')
    url = object_attributes.get('url')
    
    if not url:
        return {"status": "ignored", "reason": "missing_url"}
    
    log_context = {"server_type": "gitlab_app", "api_url": url}
    
    if action in ['open', 'reopen']:
        if is_draft(payload):
            get_logger().info(f"Skipping draft MR: {url}")
            return {"status": "ignored", "reason": "draft_mr"}
        
        await _perform_commands_gitlab("pr_commands", PRAgent(), url, log_context, payload)
        return {"status": "completed", "result": None}
    
    # For push event triggered merge requests
    elif action == 'update' and object_attributes.get('oldrev'):
        if is_draft(payload):
            get_logger().info(f"Skipping draft MR: {url}")
            return {"status": "ignored", "reason": "draft_mr"}
        
        commands_on_push = get_settings().get(f"gitlab.push_commands", {})
        handle_push_trigger = get_settings().get(f"gitlab.handle_push_trigger", False)
        
        if not commands_on_push or not handle_push_trigger:
            get_logger().info("Push event, but no push commands found or push trigger is disabled")
            return {"status": "ignored", "reason": "push_trigger_disabled"}
        
        get_logger().debug(f'A push event has been received: {url}')
        await _perform_commands_gitlab("push_commands", PRAgent(), url, log_context, payload)
        return {"status": "completed", "result": None}
    
    # For draft to ready triggered merge requests
    elif action == 'update' and is_draft_ready(payload):
        get_logger().info(f"Draft MR is ready: {url}")
        
        # Same as open MR
        await _perform_commands_gitlab("pr_commands", PRAgent(), url, log_context, payload)
        return {"status": "completed", "result": None}
    
    return {"status": "ignored", "reason": f"unsupported_action:{action}"}


async def gitlab_note_handler(payload: dict) -> dict:
    """Handler for GitLab note (comment) events."""
    if 'merge_request' not in payload:
        return {"status": "ignored", "reason": "not_merge_request_comment"}
    
    mr = payload['merge_request']
    url = mr.get('url')
    
    if not url:
        return {"status": "ignored", "reason": "missing_url"}
    
    get_logger().info(f"A comment has been added to a merge request: {url}")
    body = payload.get('object_attributes', {}).get('note')
    
    if payload.get('object_attributes', {}).get('type') == 'DiffNote' and '/ask' in body:  # /ask_line
        body = handle_ask_line(body, payload)
    
    log_context = {"server_type": "gitlab_app", "api_url": url}
    sender_id = payload.get("user", {}).get("id", "unknown")
    
    await handle_request(url, body, log_context, sender_id)
    return {"status": "completed", "result": None}


async def gitlab_fallback_handler(payload: dict) -> dict:
    """Fallback handler for other GitLab events."""
    event_type = payload.get("object_kind", "unknown")
    get_logger().info(f"Received unhandled GitLab event: {event_type}")
    return {"status": "ignored", "reason": f"unsupported_event:{event_type}"}


@router.post("/webhook")
async def gitlab_webhook(background_tasks: BackgroundTasks, request: Request):
    start_time = datetime.now()
    request_json = await request.json()
    context["settings"] = copy.deepcopy(global_settings)
    
    # Validate webhook token
    if request.headers.get("X-Gitlab-Token") and secret_provider:
        request_token = request.headers.get("X-Gitlab-Token")
        secret = secret_provider.get_secret(request_token)
        if not secret:
            get_logger().warning(f"Empty secret retrieved, request_token: {request_token}")
            return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED,
                                content=jsonable_encoder({"message": "unauthorized"}))
        try:
            secret_dict = json.loads(secret)
            gitlab_token = secret_dict["gitlab_token"]
            context["settings"].gitlab.personal_access_token = gitlab_token
        except Exception as e:
            get_logger().error(f"Failed to validate secret {request_token}: {e}")
            return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content=jsonable_encoder({"message": "unauthorized"}))
    elif get_settings().get("GITLAB.SHARED_SECRET"):
        secret = get_settings().get("GITLAB.SHARED_SECRET")
        if not request.headers.get("X-Gitlab-Token") == secret:
            get_logger().error("Failed to validate secret")
            return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content=jsonable_encoder({"message": "unauthorized"}))
    else:
        get_logger().error("Failed to validate secret")
        return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content=jsonable_encoder({"message": "unauthorized"}))
    
    gitlab_token = get_settings().get("GITLAB.PERSONAL_ACCESS_TOKEN", None)
    if not gitlab_token:
        get_logger().error("No gitlab token found")
        return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content=jsonable_encoder({"message": "unauthorized"}))
    
    # Queue the webhook for asynchronous processing
    event_type = request_json.get("object_kind", "unknown")
    webhook_processor = get_webhook_processor()
    webhook_id = await webhook_processor.enqueue_webhook("gitlab", event_type, request_json)
    
    get_logger().info(f"Queued GitLab webhook {webhook_id} of type {event_type} for asynchronous processing")
    
    end_time = datetime.now()
    get_logger().info(f"Processing time: {end_time - start_time}", request=request_json)
    
    # Return immediately to prevent webhook timeout
    return JSONResponse(status_code=status.HTTP_200_OK, 
                        content=jsonable_encoder({
                            "message": "success", 
                            "status": "queued", 
                            "webhook_id": webhook_id
                        }))


def handle_ask_line(body, data):
    try:
        line_range_ = data['object_attributes']['position']['line_range']
        # if line_range_['start']['type'] == 'new':
        start_line = line_range_['start']['new_line']
        end_line = line_range_['end']['new_line']
        # else:
        #     start_line = line_range_['start']['old_line']
        #     end_line = line_range_['end']['old_line']
        question = body.replace('/ask', '').strip()
        path = data['object_attributes']['position']['new_path']
        side = 'RIGHT'  # if line_range_['start']['type'] == 'new' else 'LEFT'
        comment_id = data['object_attributes']["discussion_id"]
        get_logger().info("Handling line comment")
        body = f"/ask_line --line_start={start_line} --line_end={end_line} --side={side} --file_name={path} --comment_id={comment_id} {question}"
    except Exception as e:
        get_logger().error(f"Failed to handle ask line comment: {e}")
    return body


@router.get("/")
async def root():
    return {"status": "ok"}

gitlab_url = get_settings().get("GITLAB.URL", None)
if not gitlab_url:
    raise ValueError("GITLAB.URL is not set")
get_settings().config.git_provider = "gitlab"
middleware = [Middleware(RawContextMiddleware)]
app = FastAPI(middleware=middleware)
app.include_router(router)


def start():
    uvicorn.run(app, host="0.0.0.0", port=3000)


if __name__ == '__main__':
    start()


# Add a new endpoint to check webhook status
@router.get("/webhook_status/{webhook_id}")
async def get_webhook_status(webhook_id: str):
    """Get the status of a webhook processing task."""
    webhook_processor = get_webhook_processor()
    status = await webhook_processor.get_webhook_status(webhook_id)
    
    if status:
        return status
    
    return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, 
                        content=jsonable_encoder({"message": "Webhook not found"}))


# Add a new endpoint to list all webhook statuses
@router.get("/webhook_statuses")
async def list_webhook_statuses():
    """List all webhook processing tasks."""
    webhook_processor = get_webhook_processor()
    statuses = await webhook_processor.get_all_webhook_statuses()
    
    return {"webhooks": statuses}


async def handle_request(api_url: str, body: str, log_context: dict, sender_id: str):
    log_context["action"] = body
    log_context["event"] = "pull_request" if body == "/review" else "comment"
    log_context["api_url"] = api_url
    log_context["app_name"] = get_settings().get("CONFIG.APP_NAME", "Unknown")

    with get_logger().contextualize(**log_context):
        await PRAgent().handle_request(api_url, body)


async def _perform_commands_gitlab(commands_conf: str, agent: PRAgent, api_url: str,
                                   log_context: dict, data: dict):
    apply_repo_settings(api_url)
    if commands_conf == "pr_commands" and get_settings().config.disable_auto_feedback:  # auto commands for PR, and auto feedback is disabled
        get_logger().info(f"Auto feedback is disabled, skipping auto commands for PR {api_url=}", **log_context)
        return
    if not should_process_pr_logic(data): # Here we already updated the configurations
        return
    commands = get_settings().get(f"gitlab.{commands_conf}", {})
    get_settings().set("config.is_auto_command", True)
    for command in commands:
        try:
            split_command = command.split(" ")
            command = split_command[0]
            args = split_command[1:]
            other_args = update_settings_from_args(args)
            new_command = ' '.join([command] + other_args)
            get_logger().info(f"Performing command: {new_command}")
            with get_logger().contextualize(**log_context):
                await agent.handle_request(api_url, new_command)
        except Exception as e:
            get_logger().error(f"Failed to perform command {command}: {e}")


def is_bot_user(data) -> bool:
    try:
        # logic to ignore bot users (unlike Github, no direct flag for bot users in gitlab)
        sender_name = data.get("user", {}).get("name", "unknown").lower()
        bot_indicators = ['codium', 'bot_', 'bot-', '_bot', '-bot']
        if any(indicator in sender_name for indicator in bot_indicators):
            get_logger().info(f"Skipping GitLab bot user: {sender_name}")
            return True
    except Exception as e:
        get_logger().error(f"Failed 'is_bot_user' logic: {e}")
    return False


def is_draft(data) -> bool:
    try:
        if 'draft' in data.get('object_attributes', {}):
            return data['object_attributes']['draft']

        # for gitlab server version before 16
        elif 'Draft:' in data.get('object_attributes', {}).get('title'):
            return True
    except Exception as e:
        get_logger().error(f"Failed 'is_draft' logic: {e}")
    return False


def is_draft_ready(data) -> bool:
    try:
        if 'draft' in data.get('changes', {}):
            if data['changes']['draft']['previous'] == 'true' and data['changes']['draft']['current'] == 'false':
                return True
            
        # for gitlab server version before 16
        elif 'title' in data.get('changes', {}):
            if 'Draft:' in data['changes']['title']['previous'] and 'Draft:' not in data['changes']['title']['current']:
                return True
    except Exception as e:
        get_logger().error(f"Failed 'is_draft_ready' logic: {e}")
    return False


def should_process_pr_logic(data) -> bool:
    try:
        if not data.get('object_attributes', {}):
            return False
        title = data['object_attributes'].get('title')
        sender = data.get("user", {}).get("username", "")

        # logic to ignore PRs from specific users
        ignore_pr_users = get_settings().get("CONFIG.IGNORE_PR_AUTHORS", [])
        if ignore_pr_users and sender:
            if sender in ignore_pr_users:
                get_logger().info(f"Ignoring PR from user '{sender}' due to 'config.ignore_pr_authors' settings")
                return False

        # logic to ignore MRs for titles, labels and source, target branches.
        ignore_mr_title = get_settings().get("CONFIG.IGNORE_PR_TITLE", [])
        ignore_mr_labels = get_settings().get("CONFIG.IGNORE_PR_LABELS", [])
        ignore_mr_source_branches = get_settings().get("CONFIG.IGNORE_PR_SOURCE_BRANCHES", [])
        ignore_mr_target_branches = get_settings().get("CONFIG.IGNORE_PR_TARGET_BRANCHES", [])

        if ignore_mr_source_branches:
            source_branch = data['object_attributes'].get('source_branch')
            if any(re.search(regex, source_branch) for regex in ignore_mr_source_branches):
                get_logger().info(
                    f"Ignoring MR with source branch '{source_branch}' due to gitlab.ignore_mr_source_branches settings")
                return False

        if ignore_mr_target_branches:
            target_branch = data['object_attributes'].get('target_branch')
            if any(re.search(regex, target_branch) for regex in ignore_mr_target_branches):
                get_logger().info(
                    f"Ignoring MR with target branch '{target_branch}' due to gitlab.ignore_mr_target_branches settings")
                return False

        if ignore_mr_labels:
            labels = [label['title'] for label in data['object_attributes'].get('labels', [])]
            if any(label in ignore_mr_labels for label in labels):
                labels_str = ", ".join(labels)
                get_logger().info(f"Ignoring MR with labels '{labels_str}' due to gitlab.ignore_mr_labels settings")
                return False

        if ignore_mr_title:
            if any(re.search(regex, title) for regex in ignore_mr_title):
                get_logger().info(f"Ignoring MR with title '{title}' due to gitlab.ignore_mr_title settings")
                return False
    except Exception as e:
        get_logger().error(f"Failed 'should_process_pr_logic': {e}")
    return True
