import unittest
from pathlib import Path
from streamlit.testing.v1 import AppTest


class DiscoveryUiTests(unittest.TestCase):
    def test_unknown_problem_then_refine_without_new_search(self):
        app = AppTest.from_file(str(Path(__file__).resolve().parents[1]/'app.py'), default_timeout=30).run()
        app.checkbox(key='demo_discovery').check().run()
        app.button(key='start_research').click().run()
        app.button(key='confirm_competitors').click().run()
        self.assertFalse(app.exception)
        self.assertEqual(app.session_state['result']['status'], 'awaiting discovery')
        app.button(key='discovery_continue').click().run()
        self.assertFalse(app.exception)
        result = app.session_state['result']
        self.assertEqual(result['decision'], 'discovery needed')
        self.assertFalse(result['hypotheses'])
        self.assertFalse(app.get('download_button'))
        profiles = result['profiles']
        app.button(key='refine_discovery').click().run()
        self.assertFalse(app.exception)
        app.text_input(key='discovery_goal').set_value('Increase funded checking relationships')
        app.text_input(key='discovery_timeframe').set_value('Next quarter')
        app.number_input(key='discovery_target').set_value(300)
        app.selectbox(key='discovery_outcome').select('Funded checking accounts')
        app.selectbox(key='discovery_problem').select('Account funding')
        app.text_area(key='discovery_observation').set_value('Illustrative client observation: applications complete but customers do not fund; validate funnel counts.')
        app.text_area(key='discovery_success').set_value('Unique accounts funded with $100 within 30 days, deduplicated across channels.')
        app.checkbox(key='discovery_confirmed').check()
        app.button(key='discovery_continue').click().run()
        self.assertFalse(app.exception)
        result = app.session_state['result']
        self.assertEqual(result['decision'], 'campaign planning ready')
        self.assertEqual(len(result['hypotheses']), 3)
        self.assertEqual(profiles, result['profiles'])
        self.assertFalse(app.get('download_button'))
        self.assertEqual(app.number_input(key='proposal_target').value,300)
        app.number_input(key='proposal_target').set_value(500).run()
        self.assertTrue(app.button(key='proposal_save').disabled)
        self.assertTrue(any('Client target is 300' in e.value for e in app.error))
        app.number_input(key='proposal_target').set_value(300).run()
        app.button(key='proposal_save').click().run()
        self.assertFalse(app.exception)
        self.assertEqual(app.session_state['result']['proposal']['inputs']['target_accounts'],300)
        app.selectbox(key='mode').select('Live research').run()
        self.assertFalse(app.exception)
        self.assertIsNone(app.session_state['result'])
        for key in ('discovery_goal', 'discovery_observation', 'discovery_success', 'discovery_confirmed'):
            with self.assertRaises(KeyError):
                app.session_state[key]

    def test_unknown_text_does_not_satisfy_readiness(self):
        from growth.discovery import discovery_questions
        questions = discovery_questions(dict(goal='More accounts', timeframe='TBD', problem='Account funding', observation='Unknown', success_definition='Not agreed', confirmed=True))
        self.assertEqual(len(questions), 3)
