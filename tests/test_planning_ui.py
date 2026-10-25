import json
import unittest
from pathlib import Path
from streamlit.testing.v1 import AppTest


class PlanningUiTests(unittest.TestCase):
    def open_report(self):
        app = AppTest.from_file(str(Path(__file__).resolve().parents[1]/'app.py'), default_timeout=30).run()
        app.button(key='start_research').click().run()
        app.button(key='confirm_competitors').click().run()
        self.assertFalse(app.exception)
        return app

    def test_paid_social_save_dirty_guard_and_approved_lock(self):
        app = self.open_report()
        self.assertEqual(app.number_input(key='proposal_direct_mail').value,70)
        app.checkbox(key='proposal_social').check().run()
        self.assertFalse(app.exception)
        self.assertEqual([app.number_input(key='proposal_'+k).value for k in ('direct_mail','display','paid_social')], [60,25,15])
        app.button(key='proposal_save').click().run()
        self.assertFalse(app.exception)
        self.assertEqual(app.session_state['result']['proposal']['scenarios'][1]['paid_social_usd'], '33750.00')
        self.assertFalse(app.checkbox(key='reviewed_evidence').value)
        app.checkbox(key='reviewed_evidence').check().run()
        app.number_input(key='proposal_target').set_value(300).run()
        app.checkbox(key='reviewed_evidence').check().run()
        self.assertTrue(app.button(key='approve_report').disabled)
        self.assertEqual(app.session_state['result']['proposal']['inputs']['target_accounts'],500)
        app.button(key='proposal_save').click().run()
        self.assertFalse(app.exception)
        self.assertFalse(app.checkbox(key='reviewed_evidence').value)
        app.checkbox(key='reviewed_evidence').check().run()
        app.checkbox(key='reviewed_target_alignment').check().run()
        app.button(key='approve_report').click().run()
        self.assertFalse(app.exception)
        result = app.session_state['result']
        self.assertEqual(result['status'],'approved')
        self.assertEqual(result['proposal']['inputs']['target_accounts'],300)
        self.assertTrue(app.number_input(key='proposal_target').disabled)
        self.assertTrue(app.button(key='proposal_save').disabled)
        self.assertEqual(len(app.get('download_button')),2)

    def test_invalid_mix_discard_and_reset(self):
        app = self.open_report()
        app.number_input(key='proposal_direct_mail').set_value(90).run()
        self.assertTrue(app.button(key='proposal_save').disabled)
        self.assertFalse(app.session_state['result'].get('proposal'))
        app.button(key='proposal_discard').click().run()
        self.assertFalse(app.exception)
        self.assertEqual(app.number_input(key='proposal_direct_mail').value,70)
        self.assertFalse(app.session_state['proposal_dirty'])
        app.button(key='proposal_save').click().run()
        app.selectbox(key='mode').select('Live research').run()
        self.assertFalse(app.exception)
        self.assertIsNone(app.session_state['result'])
        for key in ('proposal_target','proposal_note','proposal_dirty'):
            with self.assertRaises(KeyError):
                app.session_state[key]
