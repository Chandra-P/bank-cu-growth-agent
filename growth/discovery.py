"""Deterministic discovery readiness and a native strategist checkpoint."""
from .models import ClientDiscovery

PROBLEMS = ['Unknown / needs discovery', 'Awareness', 'Application completion', 'Account funding', 'Account activation']


def discovery_questions(value):
    brief = ClientDiscovery(**(value or {}))
    questions = []
    def unspecified(text):
        return text.lower().strip(' .?') in {'', 'unknown', 'unknown / needs discovery', 'none', 'not sure', 'not provided', 'tbd', 'not specified', 'not agreed', 'n/a', 'not confirmed', 'not available', 'to be confirmed', 'to be determined', 'unsure'}
    if unspecified(brief.goal) or unspecified(brief.timeframe):
        questions.append('What checking growth goal and timeframe has the client actually agreed to?')
    if brief.problem == PROBLEMS[0]:
        questions.append('Where is the observed acquisition gap: awareness, application completion, account funding or activation? Compare funnel stages before choosing a campaign.')
    if unspecified(brief.observation) or brief.problem == PROBLEMS[0]:
        questions.append('What client-reported observation or internal funnel evidence supports this diagnosis? Public competitor pages cannot establish an internal bottleneck.')
    if unspecified(brief.success_definition):
        questions.append('What exactly counts as success: opened, funded or activated accounts? Agree the funding threshold, time window, attribution and deduplication rules.')
    if not brief.confirmed:
        questions.append('Has the strategist confirmed that these fields accurately reflect client discovery, with assumptions labeled?')
    return questions


def checkpoint_form(request, profiles=None, sources=None):
    import streamlit as st
    from .report import markdown_text
    brief = ClientDiscovery(**(request.get('client_discovery') or {}))
    st.subheader('Discovery → proposal checkpoint')
    st.write('Research is ready. Confirm the client problem before generating campaigns. Unknown is an acceptable answer: the app will prepare discovery questions instead.')
    st.caption('Client-reported information is separate from public-source evidence. Business context only; do not enter customer records.')
    with st.expander('Inspect the research snapshot before confirming discovery'):
        from .report import evidence_fields
        source_map = {s['id']:s for s in (sources or [])}
        for profile in profiles or []:
            st.markdown('**'+markdown_text(profile['institution']['name'])+'**')
            supported = [(label, profile['facts'][key]) for key,label in evidence_fields(profile) if profile['facts'][key]['status']=='Source-supported']
            for label,fact in supported[:3]:
                st.write(label+': '+markdown_text(fact['value']))
                source = source_map.get(fact['source_id'])
                if source:
                    st.link_button('Inspect supporting source', source['url'])
            if not supported:
                st.caption('No supported product terms. Review source gaps before using this comparison.')
        st.caption('Public terms provide context. They do not establish the client’s internal acquisition bottleneck.')
    with st.form('discovery_checkpoint'):
        goal = st.text_input('Confirmed client goal', value=brief.goal or request.get('client_brief', '')[:500], max_chars=500, key='discovery_goal')
        timeframe = st.text_input('Goal timeframe', value=brief.timeframe, max_chars=100, key='discovery_timeframe', placeholder='For example: next quarter')
        problem = st.selectbox('Observed acquisition problem', PROBLEMS, index=PROBLEMS.index(brief.problem), key='discovery_problem')
        observation = st.text_area('Evidence or client observation supporting the problem', value=brief.observation, max_chars=1000, key='discovery_observation', placeholder='Describe the client-reported observation or internal funnel data; label assumptions.')
        metric = st.text_area('Success definition', value=brief.success_definition, max_chars=500, key='discovery_success', placeholder='Define opened, funded or activated accounts, threshold, window and deduplication.')
        constraints = st.text_area('Constraints and unresolved assumptions', value=brief.constraints, max_chars=500, key='discovery_constraints', placeholder='Budget, geography, offer, timing, channel and audience availability. Unknowns may remain.')
        confirmed = st.checkbox('I confirm this reflects client discovery; assumptions are labeled.', value=brief.confirmed, key='discovery_confirmed')
        submitted = st.form_submit_button('Continue with confirmed discovery', type='primary', key='discovery_continue')
        st.caption('Incomplete discovery produces questions, not campaigns. Research will not be repeated.')
    if submitted:
        return ClientDiscovery(goal=goal, timeframe=timeframe, problem=problem, observation=observation, success_definition=metric, constraints=constraints, confirmed=confirmed).model_dump()
    return None
