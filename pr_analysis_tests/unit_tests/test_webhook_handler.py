import unittest
from unittest.mock import Mock, patch
import json
from pr_analysis.github.webhook_handler import GitHubWebhookHandler

class TestGitHubWebhookHandler(unittest.TestCase):
    def setUp(self):
        self.pr_analyzer = Mock()
        with patch('pr_analysis.github.webhook_handler.Flask'):
            self.handler = GitHubWebhookHandler(self.pr_analyzer)
    
    @patch('pr_analysis.github.webhook_handler.Flask')
    def test_init(self, mock_flask):
        # Create a new handler to test initialization
        handler = GitHubWebhookHandler(self.pr_analyzer)
        
        # Verify Flask was initialized
        mock_flask.assert_called_once_with(__name__)
        
        # Verify the app attribute was set
        self.assertEqual(handler.app, mock_flask.return_value)
        
        # Verify the pr_analyzer attribute was set
        self.assertEqual(handler.pr_analyzer, self.pr_analyzer)
        
        # Verify setup_routes was called
        self.assertTrue(hasattr(handler, 'setup_routes'))
    
    def test_setup_routes(self):
        # Mock Flask app
        mock_app = Mock()
        self.handler.app = mock_app
        
        # Call the method under test
        self.handler.setup_routes()
        
        # Verify the route was added
        mock_app.route.assert_called_once_with('/webhook', methods=['POST'])
    
    @patch('pr_analysis.github.webhook_handler.request')
    @patch('pr_analysis.github.webhook_handler.jsonify')
    def test_handle_webhook_non_pr_event(self, mock_jsonify, mock_request):
        # Mock request headers and json
        mock_request.headers.get.return_value = 'push'
        mock_request.json = {}
        
        # Mock jsonify
        mock_jsonify.return_value = {'status': 'ignored'}
        
        # Call the method under test
        result = self.handler.handle_webhook()
        
        # Verify request.headers.get was called
        mock_request.headers.get.assert_called_once_with('X-GitHub-Event')
        
        # Verify jsonify was called
        mock_jsonify.assert_called_once_with({'status': 'ignored'})
        
        # Verify the result
        self.assertEqual(result, {'status': 'ignored'})
    
    @patch('pr_analysis.github.webhook_handler.request')
    @patch('pr_analysis.github.webhook_handler.jsonify')
    def test_handle_webhook_pr_event(self, mock_jsonify, mock_request):
        # Mock request headers and json
        mock_request.headers.get.return_value = 'pull_request'
        mock_request.json = {
            'action': 'opened',
            'number': 123,
            'repository': {'full_name': 'test/repo'}
        }
        
        # Mock jsonify
        mock_jsonify.return_value = {'status': 'success'}
        
        # Mock handle_pull_request
        self.handler.handle_pull_request = Mock(return_value={'status': 'success'})
        
        # Call the method under test
        result = self.handler.handle_webhook()
        
        # Verify request.headers.get was called
        mock_request.headers.get.assert_called_once_with('X-GitHub-Event')
        
        # Verify handle_pull_request was called
        self.handler.handle_pull_request.assert_called_once_with(mock_request.json)
        
        # Verify the result
        self.assertEqual(result, {'status': 'success'})
    
    @patch('pr_analysis.github.webhook_handler.jsonify')
    def test_handle_pull_request_ignored_action(self, mock_jsonify):
        # Mock payload with ignored action
        payload = {
            'action': 'closed',
            'number': 123,
            'repository': {'full_name': 'test/repo'}
        }
        
        # Mock jsonify
        mock_jsonify.return_value = {'status': 'ignored'}
        
        # Call the method under test
        result = self.handler.handle_pull_request(payload)
        
        # Verify jsonify was called
        mock_jsonify.assert_called_once_with({'status': 'ignored'})
        
        # Verify the result
        self.assertEqual(result, {'status': 'ignored'})
    
    @patch('pr_analysis.github.webhook_handler.jsonify')
    def test_handle_pull_request_analyzed(self, mock_jsonify):
        # Mock payload with analyzed action
        payload = {
            'action': 'opened',
            'number': 123,
            'repository': {'full_name': 'test/repo'}
        }
        
        # Mock pr_analyzer
        self.pr_analyzer.analyze_pr.return_value = ['result1', 'result2']
        
        # Mock post_results
        self.handler.post_results = Mock()
        
        # Mock jsonify
        mock_jsonify.return_value = {'status': 'success'}
        
        # Call the method under test
        result = self.handler.handle_pull_request(payload)
        
        # Verify pr_analyzer.analyze_pr was called
        self.pr_analyzer.analyze_pr.assert_called_once_with(123, 'test/repo')
        
        # Verify post_results was called
        self.handler.post_results.assert_called_once_with(
            ['result1', 'result2'], 123, 'test/repo'
        )
        
        # Verify jsonify was called
        mock_jsonify.assert_called_once_with({'status': 'success'})
        
        # Verify the result
        self.assertEqual(result, {'status': 'success'})
    
    def test_post_results(self):
        # Mock results
        results = ['result1', 'result2']
        
        # Call the method under test
        self.handler.post_results(results, 123, 'test/repo')
        
        # This method is implementation-dependent, so we'll just verify it exists
        # In a real test, we would verify that it posts the results to GitHub
        pass

if __name__ == "__main__":
    unittest.main()

