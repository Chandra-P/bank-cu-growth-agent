"""Deterministic all-in proposal scenarios, separate from research and AI costs."""
from decimal import Decimal
from pydantic import BaseModel, Field, model_validator

CHANNELS = ('direct_mail', 'display', 'paid_social')
ASSUMPTION_SOURCE = 'Strategist-provided planning assumptions; not verified performance benchmarks'


class ProposalInputs(BaseModel):
    target_accounts: int = Field(default=500, gt=0, le=1000000, strict=True)
    cpa_low: Decimal = Field(default=Decimal('300'), gt=0, le=100000, decimal_places=2)
    cpa_base: Decimal = Field(default=Decimal('450'), gt=0, le=100000, decimal_places=2)
    cpa_high: Decimal = Field(default=Decimal('600'), gt=0, le=100000, decimal_places=2)
    direct_mail_pct: int = Field(default=70, ge=0, le=100, strict=True)
    display_pct: int = Field(default=30, ge=0, le=100, strict=True)
    paid_social_pct: int = Field(default=0, ge=0, le=100, strict=True)
    include_paid_social: bool = False
    campaign: str = Field(default='Combined checking acquisition scenario', min_length=1, max_length=220)
    account_definition: str = Field(default='Unique funded consumer checking accounts; confirm funding threshold, conversion window and deduplication with the client.', min_length=1, max_length=600)
    assumption_note: str = Field(default='All-in CPA includes media, production, data, fees and incentives. No additional costs are added.', min_length=1, max_length=1000)

    @model_validator(mode='after')
    def validate_scenario(self):
        if not self.cpa_low <= self.cpa_base <= self.cpa_high:
            raise ValueError('CPA must be ordered low <= base <= high.')
        if sum(getattr(self, c+'_pct') for c in CHANNELS) != 100:
            raise ValueError('Channel allocations must total 100%.')
        if self.include_paid_social != (self.paid_social_pct > 0):
            raise ValueError('Paid social must have a positive allocation when selected and zero otherwise.')
        if not self.account_definition.strip() or not self.assumption_note.strip() or not self.campaign.strip():
            raise ValueError('Describe the account definition, scenario and assumptions.')
        return self


def calculate_proposal(inputs):
    inputs = ProposalInputs.model_validate(inputs)
    scenarios = []
    for name, cpa in (('Lower CPA', inputs.cpa_low), ('Base CPA', inputs.cpa_base), ('Higher CPA', inputs.cpa_high)):
        cents = int(cpa * inputs.target_accounts * 100)
        weights = [getattr(inputs, c+'_pct') for c in CHANNELS]
        allocations = [cents * p // 100 for p in weights]
        order = sorted(range(3), key=lambda i: cents * weights[i] % 100, reverse=True)
        for i in order[:cents - sum(allocations)]:
            allocations[i] += 1
        scenarios.append({'scenario':name, 'assumed_cpa_usd':f'{cpa:.2f}', 'total_usd':f'{Decimal(cents)/100:.2f}',
                          **{c+'_usd':f'{Decimal(n)/100:.2f}' for c,n in zip(CHANNELS, allocations)}})
    return {'inputs':inputs.model_dump(mode='json'), 'currency':'USD', 'account_type':'Funded consumer checking accounts',
            'cost_basis':'All-in; included costs are not added again', 'assumption_source':ASSUMPTION_SOURCE,
            'mix_source':'Editable planning heuristic, not an industry benchmark or optimized allocation',
            'planning_scope':'Channel mix is an independent strategist assumption. Use the combined scenario when planning across multiple concepts; confirm fit before approval.',
            'limitations':'A scenario, not a forecast or promise. Budget shares are not account contribution shares. No channel-specific CPA or expected account split is inferred.',
            'scenarios':scenarios}


def planning_available(result):
    return result.get('decision') in ('campaign planning ready', 'recorded scenario') and bool(result.get('hypotheses'))


def save_proposal(graph, config, result, inputs):
    if result.get('status') != 'awaiting review' or not planning_available(result) or result.get('approved'):
        raise ValueError('Complete discovery and campaign drafting before saving an unapproved proposal.')
    proposal = calculate_proposal(inputs)
    trace = [*result.get('trace', []), {'agent':'Strategy', 'action':'proposal:save', 'outcome':'Strategist saved assumptions; deterministic arithmetic; no API call'}]
    graph.update_state(config, {'proposal':proposal, 'trace':trace, 'approved':False, 'approval':{}})
    return dict(graph.get_state(config).values)


def mark_planner_dirty():
    import streamlit as st
    st.session_state['proposal_dirty'] = True
    st.session_state['reviewed_evidence'] = False


def change_social_mix():
    import streamlit as st
    weights = (60,25,15) if st.session_state.get('proposal_social') else (70,30,0)
    for name, value in zip(CHANNELS, weights):
        st.session_state['proposal_'+name] = value
    mark_planner_dirty()


def planner_panel(result):
    import streamlit as st
    st.subheader('Proposal planner')
    st.caption('Campaign budget planning — separate from the AI usage bill. No API calls are made by this calculator.')
    if not planning_available(result):
        st.info('Complete client discovery and campaign drafting before planning a proposal budget.')
        return None
    saved = result.get('proposal')
    defaults = ProposalInputs.model_validate(saved['inputs']) if saved else ProposalInputs()
    locked = result['status'] != 'awaiting review'
    st.info('Assumed all-in CPA: $300–$600 per funded checking account (base $450). These are strategist assumptions, not verified industry benchmarks. Included production, data, fees, incentives and media are not added a second time.')
    st.caption('Suggested allocation: 70% direct mail / 30% display; with paid social, 60% / 25% / 15%. These editable budget envelopes do not predict each channel’s account contribution.')
    settings = {'proposal_target':defaults.target_accounts, 'proposal_low':float(defaults.cpa_low), 'proposal_base':float(defaults.cpa_base), 'proposal_high':float(defaults.cpa_high),
                'proposal_social':defaults.include_paid_social, 'proposal_direct_mail':defaults.direct_mail_pct, 'proposal_display':defaults.display_pct, 'proposal_paid_social':defaults.paid_social_pct,
                'proposal_definition':defaults.account_definition, 'proposal_note':defaults.assumption_note, 'proposal_campaign':defaults.campaign}
    for key, value in settings.items():
        st.session_state.setdefault(key, value)
    st.session_state.setdefault('proposal_dirty', False)
    concepts = ['Combined checking acquisition scenario', *[h['title'] for h in result['hypotheses']]]
    if st.session_state['proposal_campaign'] not in concepts:
        st.session_state['proposal_campaign'] = concepts[0]
    st.selectbox('Campaign concept for this scenario', concepts, key='proposal_campaign', disabled=locked, on_change=mark_planner_dirty)
    st.caption('Choose the combined scenario when planning across concepts. The editable mix is a separate strategist assumption, not an automatic preferred-campaign ranking.')
    target = st.number_input('Target funded accounts (planning assumption)', min_value=1, max_value=1000000, step=1, key='proposal_target', disabled=locked, on_change=mark_planner_dirty)
    st.caption('Enter the target explicitly; it is not inferred from the client brief. Reconcile the funded-account definition with the client goal before approval.')
    cols = st.columns(3)
    low = cols[0].number_input('Lower all-in CPA ($)', min_value=0.01, max_value=100000.0, step=25.0, key='proposal_low', disabled=locked, on_change=mark_planner_dirty)
    base = cols[1].number_input('Base all-in CPA ($)', min_value=0.01, max_value=100000.0, step=25.0, key='proposal_base', disabled=locked, on_change=mark_planner_dirty)
    high = cols[2].number_input('Higher all-in CPA ($)', min_value=0.01, max_value=100000.0, step=25.0, key='proposal_high', disabled=locked, on_change=mark_planner_dirty)
    social = st.checkbox('Include paid social', key='proposal_social', disabled=locked, on_change=change_social_mix)
    cols = st.columns(3)
    mail_pct = cols[0].number_input('Direct mail allocation (%)', min_value=0, max_value=100, step=1, key='proposal_direct_mail', disabled=locked, on_change=mark_planner_dirty)
    display_pct = cols[1].number_input('Display allocation (%)', min_value=0, max_value=100, step=1, key='proposal_display', disabled=locked, on_change=mark_planner_dirty)
    social_pct = cols[2].number_input('Paid social allocation (%)', min_value=0, max_value=100, step=1, key='proposal_paid_social', disabled=locked or not social, on_change=mark_planner_dirty)
    definition = st.text_area('Funded-account definition and measurement', key='proposal_definition', max_chars=600, disabled=locked, on_change=mark_planner_dirty)
    note = st.text_area('Planning assumptions and cost inclusions', key='proposal_note', max_chars=1000, disabled=locked, on_change=mark_planner_dirty)
    preview = None
    try:
        inputs = ProposalInputs(target_accounts=target, cpa_low=str(low), cpa_base=str(base), cpa_high=str(high), include_paid_social=social,
                                direct_mail_pct=mail_pct, display_pct=display_pct, paid_social_pct=social_pct,
                                account_definition=definition, assumption_note=note, campaign=st.session_state['proposal_campaign'])
        preview = calculate_proposal(inputs)
    except ValueError:
        st.error('Check that allocations total 100%, selected paid social has a positive share, low ≤ base ≤ high CPA, and definitions are filled in.')
    if preview:
        st.markdown('**Editable preview — only the saved scenario enters the approved briefing.**')
        st.dataframe([{'Scenario':r['scenario'], 'Assumed CPA':f"${Decimal(r['assumed_cpa_usd']):,.2f}", 'All-in budget':f"${Decimal(r['total_usd']):,.2f}",
                       'Direct mail':f"${Decimal(r['direct_mail_usd']):,.2f}", 'Display':f"${Decimal(r['display_usd']):,.2f}", 'Paid social':f"${Decimal(r['paid_social_usd']):,.2f}"} for r in preview['scenarios']], hide_index=True)
        st.caption(preview['limitations'])
    if st.session_state['proposal_dirty']:
        st.warning('Planner edits are not saved. Save the scenario or discard edits before approving the brief.')
    if st.button('Save proposal scenario', key='proposal_save', type='primary', disabled=locked or preview is None):
        return inputs
    if not locked and st.session_state['proposal_dirty'] and st.button('Discard unsaved planner edits', key='proposal_discard'):
        for key in list(st.session_state):
            if key.startswith('proposal_'):
                del st.session_state[key]
        st.session_state['reviewed_evidence'] = False
        st.rerun()
    if saved:
        st.success('Saved scenario attached to this brief. Changes require saving again before approval.')
        with st.expander('Inspect saved assumptions and budgets'):
            st.json(saved, expanded=False)
    else:
        st.caption('No proposal scenario is attached yet. The briefing can still be reviewed as research only.')
    if locked:
        st.caption('This run’s proposal is locked after approval or rejection. Start a new run for a different version.')
    return None
