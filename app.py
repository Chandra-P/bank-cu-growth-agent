"""Run with: python -m streamlit run app.py"""
from pathlib import Path
from uuid import uuid4

import streamlit as st
from langgraph.types import Command
from pydantic import ValidationError

from growth.demo import DemoSearch, DemoAnalyst, demo_request
from growth.evidence import confirm_competitors, reviewed_competitor
from growth.graph import build_graph, new_state
from growth.models import Institution, ResearchRequest, FACT_FIELDS
from growth.providers import TavilySearch, LiveAnalyst
from growth.report import export_bundle, markdown_text, evidence_fields, comparison_fields
from growth.panels import activity_panel, review_panel, benchmark_panel
from growth.website import resolve_website
from growth.dashboard import overview_banner, card_surfaces
from growth.usage import summarize

ROOT = Path(__file__).resolve().parent
# Only local_app.py injects these settings. Public app.py never reads .env or
# process environment credentials, regardless of where app.py is launched.
LOCAL_SETTINGS = globals().get('_LOCAL_SETTINGS') or {}
if LOCAL_SETTINGS:
    st.session_state.setdefault('local_keys_enabled',True)
    st.session_state.setdefault('mode','Live research')
    st.session_state.setdefault('visitor_model',LOCAL_SETTINGS.get('model','gpt-6-luna'))
st.session_state.setdefault('visitor_model','gpt-6-luna')
st.set_page_config(page_title="FI growth intelligence", page_icon=":material/account_balance:", layout="wide", initial_sidebar_state="auto")
# Tables otherwise expose an independent CSV/clipboard path before review.
st.set_option("client.disableDataExport", True)

for key, value in {"graph":None, "config":None, "result":None, "run_error":None}.items():
    st.session_state.setdefault(key,value)


def reset_research():
    for key in ["graph", "config", "result", "run_error"]:
        st.session_state[key] = None
    for key in list(st.session_state):
        if key.startswith(("candidate_", "review_")) or key == "reviewed_evidence":
            del st.session_state[key]


def unconfirm_website():
    st.session_state['website_confirmed'] = False


def clear_website():
    reset_research()
    st.session_state['client_brief'] = ''
    for key in ('website_suggestion','website_usage','website_trace','website_lookup_failed'):
        st.session_state.pop(key,None)
    st.session_state['home_domain'] = ''
    unconfirm_website()


def reset_client():
    reset_research()
    clear_website()
    recorded = st.session_state.get('mode','Recorded evidence demo') == 'Recorded evidence demo'
    default = demo_request()
    st.session_state['client_name'] = default.home.name if recorded else ''
    st.session_state['client_market'] = default.market if recorded else ''
    st.session_state['client_brief'] = ''


def change_mode():
    reset_client()


def clear_credentials():
    # The graph closes over provider clients, so discard it with the keys.
    reset_client()
    st.session_state["visitor_openai_key"] = ""
    st.session_state["visitor_tavily_key"] = ""
    if LOCAL_SETTINGS:
        st.session_state['local_keys_enabled'] = False


def advance(payload):
    st.session_state.run_error = None
    try:
        with st.status("Working through the research workflow…", expanded=True) as status:
            labels = {"discover":"Discovering competitor candidates", "confirm":"Competitor set confirmed", "collect":"Collecting public-source evidence", "extract":"Checking extracted facts and research gaps", "save_profile":"Institution profile assembled", "analyze":"Drafting growth hypotheses", "review":"Review decision recorded"}
            labels.update(benchmarks='Researching public acquisition benchmarks', critique='Strategy agent reviewing the draft', revise='Revising recommendations once')
            for event in st.session_state.graph.stream(payload, st.session_state.config, stream_mode="updates"):
                for node in event:
                    if node in labels:
                        status.write(labels[node])
            st.session_state.result = dict(st.session_state.graph.get_state(st.session_state.config).values)
            status.update(label="Ready for your next decision", state="complete", expanded=False)
    except (ValueError, ValidationError, KeyError):
        st.session_state.run_error = "The input or saved response could not be validated. Check the institution names and official domains, then retry or start a new run."
    except Exception:
        st.session_state.run_error = "The run could not finish this step. Check your local configuration and provider access, then start a new run. Provider details and credentials are not displayed."


st.caption("FI GROWTH  /  RESEARCH WORKSPACE")
st.title("Growth overview")
st.caption('Checking acquisition · Competitor intelligence · Campaign planning')
card_surfaces()
current_result = st.session_state.result
current_recorded = st.session_state.get('mode', 'Recorded evidence demo') == 'Recorded evidence demo'
current_name = st.session_state.get('client_name', demo_request().home.name if current_recorded else '')
current_market = st.session_state.get('client_market', demo_request().market if current_recorded else '')
overview_banner(current_name, current_market,
                current_result['status'].capitalize() if current_result else ('Recorded demo' if current_recorded else 'Ready to research'))

active = st.session_state.result is not None
default = demo_request()
setup_region = st.expander('Client & research setup', expanded=False) if active else st.container()
setup_card = setup_region.container(border=True, key='client_setup')
with setup_card:
    st.subheader('Research setup')
    top = st.columns([3,1])
    mode = top[0].selectbox('Research mode', ['Recorded evidence demo','Live research'], key='mode', on_change=change_mode)
    top[1].button('New research', key='new_research', on_click=reset_client, disabled=not active, width='stretch')
recorded = mode == 'Recorded evidence demo'

with st.sidebar:
    st.markdown('### :material/account_balance: FI Growth')
    st.caption('STRATEGIST WORKSPACE')
    st.badge('Growth intelligence', icon=':material/dashboard:', color='blue')
    st.divider()
    st.markdown('#### Connections')
    st.caption('Choose the client and market at the top of the workspace.')
    use_local = False
    if LOCAL_SETTINGS:
        use_local = st.toggle('Use saved local keys',key='local_keys_enabled',on_change=reset_client,disabled=active)
        if use_local:
            loaded = bool(LOCAL_SETTINGS.get('openai_key') and LOCAL_SETTINGS.get('tavily_key'))
            st.success('Saved local keys connected.' if loaded else 'Some saved local keys are missing; enter the missing key below.')
        st.caption('Local launcher only. Public visitors provide their own keys. Saved key values are not placed in these inputs.')
    entered_openai = st.text_input('OpenAI API key', type='password', key='visitor_openai_key', disabled=active, max_chars=300)
    entered_tavily = st.text_input('Tavily API key', type='password', key='visitor_tavily_key', disabled=active, max_chars=300)
    openai_key = entered_openai.strip() or (LOCAL_SETTINGS.get('openai_key','') if use_local else '')
    tavily_key = entered_tavily.strip() or (LOCAL_SETTINGS.get('tavily_key','') if use_local else '')
    st.caption("Keys are sent to this app's server and held in your session memory for provider calls. Provider charges apply. They are not written to reports or saved to disk.")
    st.button('Clear keys & session',key='clear_keys',on_click=clear_credentials,width='stretch')
    with st.expander('Model settings'):
        model_name = st.text_input('OpenAI model',key='visitor_model',max_chars=100,disabled=active)
        st.caption('Public app uses visitor keys only. Local saved settings are available exclusively through the local launcher.')
    with st.expander('Session & privacy'):
        st.caption('Runs and provider clients belong to your session. Switching mode or starting new research discards the prior report and approval; keys remain until Clear keys & session. Closing a tab does not guarantee immediate cleanup.')

ready = bool(openai_key.strip() and tavily_key.strip() and model_name.strip())
if recorded:
    st.session_state.setdefault('client_name',default.home.name)
    st.session_state.setdefault('client_market',default.market)
    st.session_state['home_domain'] = default.home.domain
with setup_card:
    columns = st.columns(2)
    name = columns[0].text_input('Bank or credit union name',key='client_name',max_chars=120,disabled=recorded,on_change=clear_website,placeholder='Enter your client FI name')
    market = columns[1].text_input('Market',key='client_market',max_chars=160,disabled=recorded,on_change=clear_website,placeholder='City, state or service area')
    st.caption('Consumer checking · Direct mail, Display and Paid social')
    if recorded:
        st.info('Recorded demo uses Truliant in Charlotte. Select Live research above to choose another client.')
    else:
        if not ready:
            st.info('Connect your OpenAI and Tavily keys in the sidebar to find a website and run live research.')
        failed_lookup = st.session_state.get('website_lookup_failed',False)
        if st.button('Retry website lookup' if failed_lookup else 'Find official website',key='find_website',disabled=active or not ready or len(name.strip())<2):
            st.session_state['website_lookup_failed'] = False
            st.session_state['website_confirmed'] = False
            st.session_state['website_suggestion'] = None
            st.session_state['home_domain'] = ''
            search,analyst = TavilySearch(tavily_key.strip()),LiveAnalyst(openai_key.strip(),model_name.strip(),'https://api.openai.com/v1')
            trace = []
            try:
                with st.spinner('Finding the likely official FI website…'):
                    suggestion = resolve_website(search,analyst,name,market,trace)
                st.session_state['website_suggestion'] = suggestion
                st.session_state['home_domain'] = suggestion['institution']['domain']
            except Exception:
                st.session_state['website_lookup_failed'] = True
            finally:
                st.session_state.setdefault('website_usage',[]).extend([dict(e) for provider in (search,analyst) for e in provider.events])
                st.session_state.setdefault('website_trace',[]).extend(trace)
            # Refresh the retry label as well as the persistent error message.
            st.rerun()
        if st.session_state.get('website_lookup_failed',False):
            st.warning('Website lookup did not complete. Click Retry website lookup to try again. You can also enter the official domain manually and confirm it below.')
        suggestion = st.session_state.get('website_suggestion')
        if suggestion:
            st.write('Suggested institution: '+suggestion['institution']['name'])
            st.link_button('Inspect suggested official source',suggestion['source']['url'])
            st.caption('Source excerpt: '+suggestion['quote'])
    domain = st.text_input('Official website domain',key='home_domain',disabled=recorded or active,on_change=unconfirm_website,placeholder='Populated after website search; correct it if needed')
    valid_domain = False
    if not recorded and domain.strip():
        try:
            Institution(name=name,domain=domain)
            valid_domain = True
        except ValueError:
            st.warning('Enter a valid official public HTTPS domain.')
    confirmed = recorded
    if not recorded:
        confirmed = st.checkbox('I confirm this is the correct client FI and official website.',key='website_confirmed',disabled=active or not valid_domain)
    client_brief = st.text_area('Client goals or problem to solve',key='client_brief',max_chars=2000,disabled=active,placeholder='Annual goals, acquisition challenges and priorities. Business context only.')
    outage = False
    if recorded:
        with st.expander('Demo controls'):
            outage = st.checkbox('Simulate a Skyla source outage',key='demo_outage',disabled=active)
    start = st.button('Explore recorded demo' if recorded else 'Start live research',key='start_research',type='primary',disabled=active or (not recorded and not (ready and valid_domain and confirmed and len(market.strip())>=2)))
    if start:
        try:
            request = default if recorded else ResearchRequest(home=Institution(name=name,domain=domain,reason='Client identity and official domain confirmed by strategist'),market=market)
            request = request.model_copy(update={'client_brief':client_brief.strip()})
            if recorded:
                search,analyst = DemoSearch(outage=outage),DemoAnalyst()
            else:
                if not (ready and valid_domain and confirmed):
                    raise ValueError('Confirm client and website before research')
                search,analyst = TavilySearch(tavily_key.strip()),LiveAnalyst(openai_key.strip(),model_name.strip(),'https://api.openai.com/v1')
                for provider in (search,analyst):
                    label = 'Tavily' if provider is search else 'OpenAI'
                    provider.events.extend(dict(e) for e in st.session_state.get('website_usage',[]) if e['provider']==label)
            st.session_state.graph = build_graph(search,analyst)
            st.session_state.config = {'configurable':{'thread_id':str(uuid4())},'recursion_limit':60}
            initial = new_state(request,'recorded' if recorded else 'live')
            if not recorded:
                initial['trace'] = list(st.session_state.get('website_trace',[])) + [{'agent':'Discovery','action':'discovery:website-confirmed','outcome':'human confirmed','domain':request.home.domain}]
            advance(initial)
            st.rerun()
        except (ValueError,ValidationError):
            st.error('Check the client name, confirmed website, market and visitor keys.')

result = st.session_state.result
if st.session_state.run_error:
    st.error(st.session_state.run_error)

if not result:
    st.space("small")
    with st.container(border=True,key="scope_card"):
        st.badge("YOUR DEMO MARKET" if recorded else "YOUR RESEARCH MARKET",icon=":material/location_on:",color="blue")
        st.subheader("Truliant Federal Credit Union · Charlotte" if recorded else f"{name or 'Client not selected'} · {market or 'Choose a market'}")
        st.write("One market. Three competitors. A checking-account brief your growth team can inspect and act on.")
        st.caption("Recorded evidence demo · No API keys needed · Human approval before export" if recorded else "Live public-source research · Bring your own API keys · Human approval before export")
    st.space("small")
    st.caption(":material/arrow_back: Choose Live research and your client at the top, or explore the recorded demo. Connect live keys in the sidebar.")
    st.stop()

with st.container(horizontal=True,gap="small"):
    st.badge(result['request']['home']['name'],icon=":material/account_balance:",color="blue")
    st.badge(result['request']['market'],icon=":material/location_on:",color="blue")
if result["mode"] == "recorded":
    st.info("RECORDED DEMO · Curated evidence from October 24, 2026. No live search or model calls; recheck current terms before use.",icon=":material/history:")
else:
    st.info("LIVE RESEARCH · Model-extracted claims are checked against collected official-domain excerpts. Review current full disclosures before acting.")

status = result["status"]
st.progress({"awaiting competitors":.2,"researching":.45,"awaiting review":.85,"approved":1.,"rejected":1.}.get(status,.1), text=status.capitalize())

if status == "awaiting competitors":
    st.subheader("Confirm your comparison set")
    st.write("These are candidate alternatives, not a market-share ranking. Confirm the institution identity, local relevance and official website.")
    if not result["candidates"]:
        st.warning("Discovery did not produce a usable set. Enter three competitors manually.")
    with st.form("competitor_confirmation"):
        chosen = []
        for i in range(3):
            candidate = result["candidates"][i] if i < len(result["candidates"]) else {"name":"","domain":"","reason":"Manual selection"}
            with st.container(border=True):
                st.caption(f"COMPETITOR {i+1}")
                cols = st.columns([2,2])
                cname = cols[0].text_input("Institution name", candidate["name"], key=f"candidate_name_{i}", disabled=recorded)
                cdomain = cols[1].text_input("Official website domain", candidate["domain"], key=f"candidate_domain_{i}", disabled=recorded)
                st.caption(candidate["reason"])
                # Validate on submit below; don't attribute the old candidate's
                # discovery rationale to a manually substituted institution.
                chosen.append({"name":cname,"domain":cdomain,"candidate":candidate})
        confirmed = st.form_submit_button("Confirm and research", key="confirm_competitors", type="primary", icon=":material/play_arrow:")
    if confirmed:
        try:
            chosen = [reviewed_competitor(c["candidate"],c["name"],c["domain"]) for c in chosen]
            confirm_competitors(Institution(**result["request"]["home"]),[Institution(**c) for c in chosen])
            advance(Command(resume={"competitors":chosen}))
            st.rerun()
        except (ValueError,ValidationError):
            st.error("Enter exactly three distinct competitor names and official public domains, excluding your home institution.")
    with st.expander('Discovery activity & costs'):
        activity_panel(result)
    st.stop()

profiles = result.get("profiles",[])
facts = [f for p in profiles for f in p["facts"].values()]
supported = sum(f["status"] == "Source-supported" for f in facts)
cols = st.columns(4, gap='small')
with cols[0].container(border=True, key='kpi_institutions'):
    st.badge('RESEARCH COVERAGE', color='blue', icon=':material/account_balance:')
    st.metric("Institutions",str(len(profiles)))
with cols[1].container(border=True, key='kpi_evidence'):
    st.badge('SOURCE QUALITY', color='green', icon=':material/fact_check:')
    st.metric("Evidence",f"{supported} / {len(facts)}",help="Source-supported fields out of all compared fields.")
with cols[2].container(border=True, key='kpi_hypotheses'):
    st.badge('CAMPAIGN PLANNING', color='orange', icon=':material/campaign:')
    st.metric("Hypotheses",str(len(result["hypotheses"])))
with cols[3].container(border=True, key='kpi_cost'):
    totals = summarize(result.get('usage', []))
    st.badge('AI USAGE', color='violet', icon=':material/query_stats:')
    st.metric('Known AI subtotal' if totals['unpriced_calls'] else 'AI model cost', f"${totals['total_cost_usd']:.6f}")
    st.caption('Partial estimate · inspect activity' if totals['unpriced_calls'] else 'Recorded replay · no API calls' if result['mode']=='recorded' else 'Includes cache writes · search billed separately')

brief, evidence, benchmarks, revisions, trace, method = st.tabs(["Comparison & opportunities","Evidence & gaps","Benchmarks","Review & revision","Agent activity & costs","How it works"])
with brief:
    with st.container(border=True, key='takeaway_card'):
        st.subheader('Strategist takeaway')
        st.caption('CLIENT CONTEXT · provided by the strategist')
        st.write(markdown_text(result['request'].get('client_brief') or 'Not provided; confirm the client goal and problem.'))
        takeaway = result.get('strategist_takeaway')
        if takeaway:
            st.markdown('**Research finding:** '+markdown_text(takeaway['finding']))
            st.markdown('**Strategic implication:** '+markdown_text(takeaway['implication']))
            st.markdown('**Client validation question:** '+markdown_text(takeaway['client_question']))
            st.caption('Evidence: '+', '.join(takeaway['source_ids']))
        else:
            st.info('A supported takeaway is unavailable; review the comparison and gaps.')
        if result['mode']=='recorded':
            st.caption('Curated examples are not personalized to the entered client context. Live mode uses the client brief.')
    with st.container(border=True,key="comparison_card"):
        st.badge("MARKET SNAPSHOT",icon=":material/compare_arrows:",color="blue")
        st.subheader("How the checking offers compare")
        rows = [{"Field":label, **{p["institution"]["name"]:p["facts"][key]["value"] for p in profiles}} for key,label in comparison_fields(profiles)]
        st.caption('Rows with the most source-supported claims appear first.')
        st.dataframe(rows,hide_index=True,height=365,alt="Checking product comparison for the home institution and three confirmed competitors")
        st.caption("Not verified = insufficient evidence. It does not mean zero fees, no requirement, or no available offer.")
    st.subheader("Campaign concepts for the client discussion")
    st.caption("Inference for human review · no promised uplift or unverified claims of product superiority")
    opportunity_columns = st.columns(3, gap="medium")
    for i,h in enumerate(result["hypotheses"],1):
        with opportunity_columns[(i-1) % 3].container(border=True,key=f"opportunity_card_{i}"):
            st.badge(f"OPPORTUNITY {i:02d}",icon=":material/experiment:",color="blue")
            st.markdown(f"#### {i}. {markdown_text(h['title'])}")
            st.write(markdown_text(h["rationale"]))
            st.markdown('**Audience:** '+markdown_text(h.get('audience','To confirm')))
            st.markdown('**Client need:** '+markdown_text(h.get('need_connection','To confirm')))
            st.markdown('**Message:** '+markdown_text(h.get('message','To develop')))
            st.caption('CHANNELS · '+', '.join(h.get('channels',[])))
            st.write(markdown_text(h.get('channel_rationale','To confirm')))
            with st.expander("Experiment & success metric"):
                st.caption("THE EXPERIMENT")
                st.write(markdown_text(h["experiment"]))
                st.caption("WHAT TO MEASURE")
                st.write(markdown_text(h["success_metric"]))
                st.markdown('**Guardrail:** '+markdown_text(h.get('guardrail','To confirm')))
                st.markdown('**Ask the client:** '+markdown_text(h.get('client_question','Confirm the goal.')))
            with st.expander("Evidence & limitations",icon=":material/policy:"):
                st.caption("Limit: " + markdown_text(h["caveat"]))
                st.caption("Evidence: " + ", ".join(h["source_ids"]))
    if result["warnings"]:
        with st.expander("Research limitations",expanded=True):
            for warning in result["warnings"]:
                st.warning(warning)

with evidence:
    st.subheader("Follow each finding to its source")
    st.caption('Source-supported claims appear first in each institution; unverified claims follow.')
    st.caption("The checks enforce source identity, an exact excerpt match, and numeric consistency. They do not establish semantic correctness or completeness; human review remains necessary.")
    sources = {s["id"]:s for s in result["sources"]}
    for profile in profiles:
        with st.expander(profile["institution"]["name"],expanded=False):
            for key,label in evidence_fields(profile):
                fact = profile["facts"][key]
                st.markdown(f"**{label}:** {markdown_text(fact['value'])}")
                if fact["status"] == "Source-supported":
                    source = sources[fact["source_id"]]
                    st.text(f"Supporting excerpt: {fact['quote']}")
                    st.link_button("Open official source",source["url"],icon=":material/open_in_new:")
                    st.caption(f"{source['id']} · Retrieved {source['retrieved_at']} · {source['collection']}")
            st.caption("Gaps: " + ", ".join(profile["gaps"]))

with trace:
    activity_panel(result)

with benchmarks:
    benchmark_panel(result)

with revisions:
    review_panel(result)

with method:
    st.subheader("A small, stateful agent system")
    st.code("Discovery → HUMAN CONFIRMS → Research → Strategy draft\n    → Benchmarks → Strategy review → One revision → HUMAN APPROVES → Export",language=None)
    st.write('Discovery proposes competitors. Research collects official checking evidence and selects one useful follow-up per institution. Strategy connects findings to client needs. Benchmarks researches public acquisition economics. Strategy reviews and revises once. These are four logical roles sharing a model client, not four servers. LangGraph manages state and human checkpoints.')
    st.write('Tool use is orchestrated Python API calls, not autonomous model function-calling. Models propose structured research decisions; the graph validates and executes them. Cost tracking is session-local; no external tracing account is required.')
    st.write("Limits: three competitors, two search rounds per institution, five results per search, one retry per remote operation. Memory is scoped to this session. Public product evidence only; no campaign publishing.")

st.divider()
if status == "awaiting review":
    with st.container(border=True,key="review_card"):
        st.badge("HUMAN CHECKPOINT",icon=":material/verified_user:",color="blue")
        st.subheader("Ready to share this brief?")
        st.write("Review the evidence, missing terms and proposed tests. Your approval enables downloads; it does not publish a campaign.")
        note = st.text_area("Reviewer notes",key="review_note",max_chars=1000,placeholder="Record caveats or follow-up checks for your team.")
        reviewed = st.checkbox("I reviewed the evidence and understand the gaps and hypotheses.",key="reviewed_evidence")
        with st.container(horizontal=True):
            approve = st.button("Approve and enable downloads",key="approve_report",type="primary",disabled=not reviewed,icon=":material/check:")
            reject = st.button("Reject this brief",key="reject_report",icon=":material/close:")
    if approve or reject:
        advance(Command(resume={"approve":bool(approve and reviewed),"note":note}))
        st.rerun()
elif status == "approved":
    st.success("Approved for export. The report retains its evidence, limitations and reviewer note.")
    md,js = export_bundle(result)
    with st.container(horizontal=True):
        st.download_button("Download briefing",md,file_name="checking-growth-brief.md",mime="text/markdown",key="download_brief",icon=":material/download:")
        st.download_button("Download evidence & trace",js,file_name="checking-growth-evidence.json",mime="application/json",key="download_evidence",icon=":material/data_object:")
elif status == "rejected":
    st.warning("Brief rejected. Downloads are unavailable. Start new research to change the scope or collect better evidence.")
