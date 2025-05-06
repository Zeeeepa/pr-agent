import hashlib
import hmac
import json
import unittest
from unittest.mock import patch, MagicMock

from fastapi import HTTPException
from pr_agent.servers.utils import verify_signature


class WebhookValidationTest(unittest.TestCase):
    """Test cases for webhook signature validation."""

    def test_valid_signature(self):
        """Test that a valid signature passes verification."""
        # Setup
        secret = "test_secret"
        payload = b'{"action": "opened", "pull_request": {"url": "https://api.github.com/repos/test/test/pulls/1"}}'
        
        # Generate a valid signature
        hash_object = hmac.new(secret.encode('utf-8'), msg=payload, digestmod=hashlib.sha256)
        signature = "sha256=" + hash_object.hexdigest()
        
        # Verify - should not raise an exception
        try:
            verify_signature(payload, secret, signature)
            passed = True
        except HTTPException:
            passed = False
        
        self.assertTrue(passed, "Valid signature should pass verification")

    def test_invalid_signature(self):
        """Test that an invalid signature fails verification."""
        # Setup
        secret = "test_secret"
        payload = b'{"action": "opened", "pull_request": {"url": "https://api.github.com/repos/test/test/pulls/1"}}'
        
        # Generate an invalid signature
        signature = "sha256=invalid_signature"
        
        # Verify - should raise an HTTPException
        with self.assertRaises(HTTPException) as context:
            verify_signature(payload, secret, signature)
        
        self.assertEqual(context.exception.status_code, 403, "Invalid signature should return 403")
        self.assertEqual(context.exception.detail, "Request signatures didn't match!", 
                         "Error message should indicate signature mismatch")

    def test_missing_signature(self):
        """Test that a missing signature header fails verification."""
        # Setup
        secret = "test_secret"
        payload = b'{"action": "opened", "pull_request": {"url": "https://api.github.com/repos/test/test/pulls/1"}}'
        
        # Verify with None signature - should raise an HTTPException
        with self.assertRaises(HTTPException) as context:
            verify_signature(payload, secret, None)
        
        self.assertEqual(context.exception.status_code, 403, "Missing signature should return 403")
        self.assertEqual(context.exception.detail, "x-hub-signature-256 header is missing!", 
                         "Error message should indicate missing header")


class AsyncWebhookHandlingTest(unittest.TestCase):
    """Test cases for asynchronous webhook handling."""
    
    @patch('pr_agent.servers.github_app.handle_request')
    async def test_webhook_background_processing(self, mock_handle_request):
        """Test that webhooks are processed in the background."""
        from pr_agent.servers.github_app import handle_github_webhooks
        from fastapi import Request, Response
        from starlette.background import BackgroundTasks
        
        # Setup
        background_tasks = BackgroundTasks()
        request = MagicMock(spec=Request)
        response = MagicMock(spec=Response)
        
        # Mock the request body
        request.json.return_value = {
            "action": "opened",
            "pull_request": {"url": "https://api.github.com/repos/test/test/pulls/1"},
            "installation": {"id": "12345"}
        }
        request.headers = {"X-GitHub-Event": "pull_request"}
        request.body.return_value = json.dumps(request.json.return_value).encode()
        
        # Call the webhook handler
        result = await handle_github_webhooks(background_tasks, request, response)
        
        # Verify background task was added
        self.assertTrue(background_tasks.tasks, "Background task should be added")
        self.assertEqual(result, {}, "Response should be empty dict")


if __name__ == '__main__':
    unittest.main()

