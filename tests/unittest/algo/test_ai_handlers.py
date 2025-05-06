import unittest
from unittest.mock import patch, MagicMock

from pr_agent.algo.ai_handlers.base_ai_handler import BaseAiHandler
from pr_agent.algo.ai_handlers.litellm_ai_handler import LiteLLMAIHandler
from pr_agent.algo.ai_handlers.openai_ai_handler import OpenAIAIHandler
from pr_agent.algo.ai_handlers.langchain_ai_handler import LangchainAIHandler


class TestAIHandlers(unittest.TestCase):
    """
    Test cases for the AI handlers.
    """
    
    @patch('pr_agent.algo.ai_handlers.litellm_ai_handler.get_settings')
    def test_litellm_ai_handler_initialization(self, mock_get_settings):
        """
        Test that LiteLLMAIHandler initializes correctly.
        """
        # Mock settings
        mock_settings = MagicMock()
        mock_settings.get.return_value = "test_key"
        mock_get_settings.return_value = mock_settings
        
        # Initialize handler
        handler = LiteLLMAIHandler()
        
        # Verify initialization
        self.assertIsInstance(handler, BaseAiHandler)
        
    @patch('pr_agent.algo.ai_handlers.openai_ai_handler.get_settings')
    def test_openai_ai_handler_initialization(self, mock_get_settings):
        """
        Test that OpenAIAIHandler initializes correctly.
        """
        # Mock settings
        mock_settings = MagicMock()
        mock_settings.get.return_value = "test_key"
        mock_get_settings.return_value = mock_settings
        
        # Initialize handler
        handler = OpenAIAIHandler()
        
        # Verify initialization
        self.assertIsInstance(handler, BaseAiHandler)
        
    @patch('pr_agent.algo.ai_handlers.langchain_ai_handler.get_settings')
    def test_langchain_ai_handler_initialization(self, mock_get_settings):
        """
        Test that LangchainAIHandler initializes correctly.
        """
        # Mock settings
        mock_settings = MagicMock()
        mock_settings.get.return_value = "test_key"
        mock_get_settings.return_value = mock_settings
        
        # Initialize handler
        handler = LangchainAIHandler()
        
        # Verify initialization
        self.assertIsInstance(handler, BaseAiHandler)
        
    @patch('pr_agent.algo.ai_handlers.litellm_ai_handler.get_settings')
    @patch('pr_agent.algo.ai_handlers.litellm_ai_handler.acompletion')
    async def test_litellm_chat_completion(self, mock_acompletion, mock_get_settings):
        """
        Test that LiteLLMAIHandler.chat_completion works correctly.
        """
        # Mock settings
        mock_settings = MagicMock()
        mock_settings.get.return_value = "test_key"
        mock_get_settings.return_value = mock_settings
        
        # Mock acompletion response
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message = MagicMock()
        mock_response.choices[0].message.content = "AI response"
        mock_acompletion.return_value = mock_response
        
        # Initialize handler
        handler = LiteLLMAIHandler()
        
        # Call chat_completion
        result = await handler.chat_completion(
            model="gpt-4",
            system="You are a helpful assistant.",
            user="What is the meaning of life?",
            temperature=0.2
        )
        
        # Verify result
        self.assertEqual(result, "AI response")
        
        # Verify acompletion was called with correct parameters
        mock_acompletion.assert_called_once()
        call_args = mock_acompletion.call_args[1]
        self.assertEqual(call_args["model"], "gpt-4")
        self.assertEqual(call_args["temperature"], 0.2)
        self.assertEqual(len(call_args["messages"]), 2)
        self.assertEqual(call_args["messages"][0]["role"], "system")
        self.assertEqual(call_args["messages"][0]["content"], "You are a helpful assistant.")
        self.assertEqual(call_args["messages"][1]["role"], "user")
        self.assertEqual(call_args["messages"][1]["content"], "What is the meaning of life?")
        
    @patch('pr_agent.algo.ai_handlers.litellm_ai_handler.get_settings')
    @patch('pr_agent.algo.ai_handlers.litellm_ai_handler.acompletion')
    async def test_litellm_chat_completion_with_reasoning_effort(self, mock_acompletion, mock_get_settings):
        """
        Test that LiteLLMAIHandler.chat_completion works correctly with reasoning effort.
        """
        # Mock settings
        mock_settings = MagicMock()
        mock_settings.get.return_value = "test_key"
        mock_settings.config.reasoning_effort = "high"
        mock_get_settings.return_value = mock_settings
        
        # Mock acompletion response
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message = MagicMock()
        mock_response.choices[0].message.content = "AI response with high reasoning"
        mock_acompletion.return_value = mock_response
        
        # Initialize handler
        handler = LiteLLMAIHandler()
        
        # Call chat_completion
        result = await handler.chat_completion(
            model="claude-3-opus-20240229",
            system="You are a helpful assistant.",
            user="What is the meaning of life?",
            temperature=0.2
        )
        
        # Verify result
        self.assertEqual(result, "AI response with high reasoning")
        
        # Verify acompletion was called with correct parameters
        mock_acompletion.assert_called_once()
        call_args = mock_acompletion.call_args[1]
        self.assertEqual(call_args["model"], "claude-3-opus-20240229")
        self.assertEqual(call_args["temperature"], 0.2)
        self.assertEqual(len(call_args["messages"]), 2)
        self.assertEqual(call_args["messages"][0]["role"], "system")
        self.assertTrue("reasoning_effort: high" in call_args["messages"][0]["content"])
        self.assertEqual(call_args["messages"][1]["role"], "user")
        self.assertEqual(call_args["messages"][1]["content"], "What is the meaning of life?")


if __name__ == '__main__':
    unittest.main()

