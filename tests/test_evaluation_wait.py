import unittest
from types import SimpleNamespace
from evals.run_quality import wait_for_baseline

class EvaluationWaitTests(unittest.TestCase):
    def test_evidence_without_result_times_out(self):
        exists=SimpleNamespace(exists=lambda:True)
        missing=SimpleNamespace(exists=lambda:False)
        with self.assertRaises(TimeoutError):wait_for_baseline(exists,missing,seconds=0)

    def test_complete_pair_does_not_wait(self):
        exists=SimpleNamespace(exists=lambda:True)
        wait_for_baseline(exists,exists,seconds=0)
