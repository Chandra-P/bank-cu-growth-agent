import unittest
from unittest.mock import Mock, patch
from pathlib import Path
from streamlit.testing.v1 import AppTest
from growth.models import Institution, Source


class ClientSelectionTests(unittest.TestCase):
    def test_switching_to_live_discards_demo_report_and_approval(self):
        app=AppTest.from_file(str(Path(__file__).resolve().parents[1]/'app.py'),default_timeout=30).run()
        app.button(key='start_research').click().run()
        app.button(key='confirm_competitors').click().run()
        self.assertEqual(app.session_state['result']['status'],'awaiting review')
        app.selectbox(key='mode').select('Live research').run()
        self.assertFalse(app.exception)
        self.assertIsNone(app.session_state['result'])
        self.assertIsNone(app.session_state['graph'])
        self.assertIsNone(app.session_state['config'])
        self.assertEqual(app.text_input(key='client_name').value,'')
        self.assertEqual(app.text_input(key='home_domain').value,'')
        self.assertFalse(app.get('download_button'))
        self.assertNotIn('Strategist takeaway',[s.value for s in app.subheader])

    def test_changing_live_client_clears_an_active_report(self):
        app=AppTest.from_file(str(Path(__file__).resolve().parents[1]/'app.py'),default_timeout=30).run()
        app.button(key='start_research').click().run()
        app.button(key='confirm_competitors').click().run()
        report=dict(app.session_state['result'])
        app.selectbox(key='mode').select('Live research').run()
        report['mode']='live'
        app.session_state['result']=report
        app.run()
        self.assertFalse(app.text_input(key='client_name').disabled)
        app.text_input(key='client_name').set_value('Different Bank').run()
        self.assertFalse(app.exception)
        self.assertIsNone(app.session_state['result'])
        self.assertIsNone(app.session_state['graph'])
        self.assertFalse(app.get('download_button'))

    def test_top_level_selection_requires_confirmation_and_invalidates_edits(self):
        app=AppTest.from_file(str(Path(__file__).resolve().parents[1]/'app.py'),default_timeout=30).run()
        self.assertTrue(app.main.selectbox(key='mode'))
        app.selectbox(key='mode').select('Live research').run()
        app.text_input(key='visitor_openai_key').set_value('test-openai').run()
        app.text_input(key='visitor_tavily_key').set_value('test-tavily').run()
        app.text_input(key='client_name').set_value('Example Credit Union').run()
        app.text_input(key='client_market').set_value('Charlotte, NC').run()
        self.assertTrue(app.button(key='start_research').disabled)
        with patch('growth.website.resolve_website') as resolve:
            resolve.return_value={'institution':Institution(name='Example Credit Union',domain='example.org').model_dump(),'source':{'title':'Official site','url':'https://example.org/','excerpt':'Example Credit Union'},'quote':'Example Credit Union'}
            app.button(key='find_website').click().run()
        self.assertFalse(app.exception)
        self.assertEqual(app.text_input(key='home_domain').value,'example.org')
        self.assertTrue(app.button(key='start_research').disabled)
        app.checkbox(key='website_confirmed').check().run()
        self.assertFalse(app.button(key='start_research').disabled)
        app.text_input(key='home_domain').set_value('different.org').run()
        self.assertFalse(app.checkbox(key='website_confirmed').value)
        app.checkbox(key='website_confirmed').check().run()
        app.text_input(key='client_name').set_value('Another Credit Union').run()
        self.assertEqual(app.text_input(key='home_domain').value,'')
        self.assertTrue(app.button(key='start_research').disabled)

    def test_website_suggestion_requires_matching_source_domain_and_quote(self):
        from growth.models import WebsiteSuggestion
        from growth.website import resolve_website
        source=Source(id='s1',title='Directory',url='https://directory.org/',excerpt='Example Credit Union',retrieved_at='2026-10-24')
        search,analyst=Mock(),Mock()
        search.search.return_value=[source]
        analyst.resolve_website.return_value=WebsiteSuggestion(institution=Institution(name='Example Credit Union',domain='example.org'),source_id='s1',quote='Example Credit Union')
        with self.assertRaises(ValueError):
            resolve_website(search,analyst,'Example Credit Union','Charlotte',[])

    def test_directory_only_search_can_recover_with_one_official_domain_follow_up(self):
        from growth.models import WebsiteSuggestion
        from growth.website import resolve_website
        directory=Source(id='directory',title='Directory',url='https://directory.org/',excerpt='Example Credit Union',retrieved_at='2026-10-24')
        official=Source(id='official',title='Example Credit Union',url='https://example.org/',excerpt='Welcome to Example Credit Union',retrieved_at='2026-10-24')
        institution=Institution(name='Example Credit Union',domain='example.org')
        search,analyst=Mock(),Mock()
        search.search.side_effect=[[directory],[official]]
        analyst.resolve_website.side_effect=[WebsiteSuggestion(institution=institution,source_id='missing',quote='Not verified'),WebsiteSuggestion(institution=institution,source_id='official',quote='Welcome to Example Credit Union')]
        result=resolve_website(search,analyst,'Example Credit Union','Charlotte',[])
        self.assertEqual(result['institution']['domain'],'example.org')
        self.assertEqual(search.search.call_count,2)
        self.assertEqual(search.search.call_args.args[1],'example.org')


if __name__=='__main__':
    unittest.main()
