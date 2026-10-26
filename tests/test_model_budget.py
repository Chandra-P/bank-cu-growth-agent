import unittest
from unittest.mock import patch
from growth.providers import LiveAnalyst

class ModelBudgetTests(unittest.TestCase):
    def test_reasoning_requests_use_evaluated_completion_budget(self):
        with patch('growth.providers.ChatOpenAI') as client:
            LiveAnalyst('test-not-a-real-key','gpt-6-luna')
        kwargs=client.call_args.kwargs
        self.assertEqual(kwargs['timeout'],120)
        self.assertEqual(kwargs['max_tokens'],8000)
        self.assertEqual(kwargs['reasoning_effort'],'low')
        self.assertNotIn('temperature',kwargs)

    def test_non_reasoning_models_do_not_receive_reasoning_effort(self):
        with patch('growth.providers.ChatOpenAI') as client:
            LiveAnalyst('test-not-a-real-key','nonreasoning-test-model')
        self.assertNotIn('reasoning_effort',client.call_args.kwargs)
