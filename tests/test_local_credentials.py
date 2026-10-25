import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from streamlit.testing.v1 import AppTest

ROOT=Path(__file__).resolve().parents[1]


class LocalCredentialsTests(unittest.TestCase):
    def test_public_entry_never_reads_saved_local_settings(self):
        with patch('growth.local_config.read_local_settings',side_effect=AssertionError('Public app must not read .env')):
            app=AppTest.from_file(str(ROOT/'app.py'),default_timeout=30).run()
            self.assertFalse(app.exception)
            self.assertEqual(app.text_input(key='visitor_openai_key').value,'')
            self.assertEqual(app.text_input(key='visitor_tavily_key').value,'')

    def test_local_entry_uses_keys_without_putting_them_in_widgets_and_clear_disables(self):
        import streamlit as st
        real_get=st.get_option
        def get_option(name):
            return '127.0.0.1' if name=='server.address' else real_get(name)
        with patch('streamlit.get_option',side_effect=get_option), patch('growth.local_config.read_local_settings',return_value={'openai_key':'local-openai-sentinel','tavily_key':'local-tavily-sentinel','model':'gpt-6-luna'}):
            app=AppTest.from_file(str(ROOT/'local_app.py'),default_timeout=30).run()
            self.assertFalse(app.exception)
            self.assertEqual(app.selectbox(key='mode').value,'Live research')
            self.assertEqual(app.text_input(key='visitor_openai_key').value,'')
            app.text_input(key='client_name').set_value('United Heritage Credit Union').run()
            self.assertFalse(app.button(key='find_website').disabled)
            app.button(key='clear_keys').click().run()
            self.assertFalse(app.exception)
            self.assertFalse(app.toggle(key='local_keys_enabled').value)
            self.assertTrue(app.button(key='find_website').disabled)

    def test_local_entry_refuses_network_binding_before_reading_keys(self):
        import streamlit as st
        real_get=st.get_option
        def get_option(name):
            return '0.0.0.0' if name=='server.address' else real_get(name)
        with patch('streamlit.get_option',side_effect=get_option),patch('growth.local_config.read_local_settings') as loader:
            app=AppTest.from_file(str(ROOT/'local_app.py'),default_timeout=30).run()
            self.assertFalse(app.exception)
            loader.assert_not_called()
            self.assertTrue(any('loopback' in e.value for e in app.error))

