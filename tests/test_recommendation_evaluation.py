import unittest
from evals.scoring import aggregate, outcome

class RecommendationEvaluationTests(unittest.TestCase):
    def test_threshold_requires_all_dimensions(self):
        self.assertFalse(outcome([4,4,4,4,4,1], [], True)['passed'])
        self.assertTrue(outcome([3,3,3,3,3,3], [], True)['passed'])

    def test_critical_failure_cannot_be_outscored(self):
        result=outcome([4]*6, ['Unsupported material product claim'], True)
        self.assertEqual(result['score'],100)
        self.assertFalse(result['passed'])

    def test_structural_failure_blocks_pass(self):
        self.assertFalse(outcome([4]*6, [], False)['passed'])

    def test_incomplete_judging_rejected(self):
        for values in ([4]*5, [4]*7, [4,4,4,4,4,5], [True]*6):
            with self.assertRaises(ValueError):outcome(values, [], True)

    def test_failed_cases_stay_in_denominator(self):
        result=aggregate([{'final':{'score':90,'passed':True,'critical_flags':[]}}, {'final':None}], expected=2)
        self.assertEqual(result['pass_rate_pct'],50)
        self.assertEqual(result['mean_score_all_cases'],45)
        self.assertEqual(result['failed_or_unscored_cases'],1)

    def test_incomplete_suite_not_presented_complete(self):
        with self.assertRaises(ValueError):aggregate([],expected=10)
