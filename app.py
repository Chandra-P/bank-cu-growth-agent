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
from growth.report import export_bundle, markdown_text
from growth.panels import activity_panel, review_panel, benchmark_panel
from growth.website import resolve_website

ROOT = Path(__file__).resolve().parent
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
    for key in ('website_suggestion','website_usage','website_trace'):
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


st.caption("FI / GROWTH     ·     WORKSPACE / COMPETITOR ANALYSIS")
st.title("Your market, in focus.")
st.markdown("Consumer checking intelligence for banks and credit unions.")
st.caption('Four-agent workflow · Review & revision · Usage transparency')

active = st.session_state.result is not None
default = demo_request()
with st.container(border=True):
    st.subheader('Choose your client')
    top = st.columns([3,1])
    mode = top[0].selectbox('Research mode', ['Recorded evidence demo','Live research'], key='mode', on_change=change_mode)
    top[1].button('New research', key='new_research', on_click=reset_client, disabled=not active, width='stretch')
recorded = mode == 'Recorded evidence demo'

with st.sidebar:
    st.badge('FI / GROWTH',icon=':material/account_balance:',color='blue')
    st.markdown('## Research connections')
    st.caption('Choose the client and market at the top of the workspace.')
    openai_key = st.text_input('OpenAI API key', type='password', key='visitor_openai_key', disabled=active, max_chars=300)
    tavily_key = st.text_input('Tavily API key', type='password', key='visitor_tavily_key', disabled=active, max_chars=300)
    st.caption("Keys are sent to this app's server and held in your session memory for provider calls. Provider charges apply. They are not written to reports or saved to disk.")
    st.button('Clear keys & session',key='clear_keys',on_click=clear_credentials,width='stretch')
    with st.expander('Model settings'):
        model_name = st.text_input('OpenAI model','gpt-6-luna',key='visitor_model',max_chars=100,disabled=active)
        st.caption('Keys are never loaded from the host environment.')
    with st.expander('Session & privacy'):
        st.caption('Runs and provider clients belong to your session. Switching mode or starting new research discards the prior report and approval; keys remain until Clear keys & session. Closing a tab does not guarantee immediate cleanup.')

ready = bool(openai_key.strip() and tavily_key.strip() and model_name.strip())
if recorded:
    st.session_state.setdefault('client_name',default.home.name)
    st.session_state.setdefault('client_market',default.market)
    st.session_state['home_domain'] = default.home.domain
with st.container(border=True,key='client_setup'):
    columns = st.columns(2)
    name = columns[0].text_input('Bank or credit union name',key='client_name',max_chars=120,disabled=recorded,on_change=clear_website,placeholder='Enter your client FI name')
    market = columns[1].text_input('Market',key='client_market',max_chars=160,disabled=recorded,on_change=clear_website,placeholder='City, state or service area')
    st.caption('Consumer checking · Direct mail, Display and Paid social')
    if recorded:
        st.info('Recorded demo uses Truliant in Charlotte. Select Live research above to choose another client.')
    else:
        if not ready:
            st.info('Connect your OpenAI and Tavily keys in the sidebar to find a website and run live research.')
        if st.button('Find official website',key='find_website',disabled=active or not ready or len(name.strip())<2):
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
                st.warning('A supported website suggestion was unavailable. Enter the official domain manually and confirm it below.')
            finally:
                st.session_state.setdefault('website_usage',[]).extend([dict(e) for provider in (search,analyst) for e in provider.events])
                st.session_state.setdefault('website_trace',[]).extend(trace)
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
    steps = st.columns(4,gap="medium")
    with steps[0].container(border=True):
        st.badge("01 / DISCOVER",icon=":material/travel_explore:",color="blue")
        st.subheader("Map your alternatives")
        st.write("Review three candidate institutions and confirm the market you want to compare.")
    with steps[1].container(border=True):
        st.badge("02 / COMPARE",icon=":material/fact_check:",color="blue")
        st.subheader("See the terms clearly")
        st.write("Compare checking products with source evidence and explicit gaps.")
    with steps[2].container(border=True):
        st.badge("03 / STRATEGY",icon=":material/experiment:",color="blue")
        st.subheader("Choose what to test")
        st.write("Review growth hypotheses, experiments and metrics before sharing your brief.")
    with steps[3].container(border=True):
        st.badge('04 / BENCHMARKS',icon=':material/query_stats:',color='blue')
        st.subheader('Ground the economics')
        st.write('Research public CPA evidence, then inspect the strategy review and revision before approving.')
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
with st.container(horizontal=True, gap="small", wrap=True):
    cols = [st.container(width=210) for _ in range(4)]
cols[0].metric("Institutions",str(len(profiles)),border=True)
cols[1].metric("Evidence",f"{supported} / {len(facts)}",border=True,help="Source-supported fields out of all compared fields.")
cols[2].metric("Hypotheses",str(len(result["hypotheses"])),border=True)
cols[3].metric("Review status",status.removeprefix("awaiting ").capitalize(),border=True)

brief, evidence, benchmarks, revisions, trace, method = st.tabs(["Comparison & opportunities","Evidence & gaps","Benchmarks","Review & revision","Agent activity & costs","How it works"])
with brief:
    with st.container(border=True):
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
        rows = [{"Field":label, **{p["institution"]["name"]:p["facts"][key]["value"] for p in profiles}} for key,label in FACT_FIELDS.items()]
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
    st.caption("The checks enforce source identity, an exact excerpt match, and numeric consistency. They do not establish semantic correctness or completeness; human review remains necessary.")
    sources = {s["id"]:s for s in result["sources"]}
    for profile in profiles:
        with st.expander(profile["institution"]["name"],expanded=False):
            for key,label in FACT_FIELDS.items():
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
