"""Native Streamlit views for evidence, review and provider usage."""
import streamlit as st
from .report import markdown_text
from .usage import summarize, PRICE_SOURCE, PRICE_DATE


def activity_panel(result):
    st.subheader('Agent activity & AI costs')
    st.caption('Four logical agents coordinated by LangGraph. Strategy performs the review and one revision; it is not a fifth agent.')
    st.caption('Live cost estimates include ordinary input, cache reads, cache writes and output. Cache writes are part of input cost and are counted once.')
    st.code('Discovery → Human confirms → Research → Strategy draft\n    → Benchmarks → Strategy review → One revision → Human approval', language=None)
    records = result.get('usage', [])
    totals = summarize(records)
    if result['mode']=='recorded':
        st.info('Recorded replay · 0 external API calls · $0 AI cost. Steps below are local fixture operations; no token counts are simulated.')
    else:
        with st.container(horizontal=True, wrap=True):
            st.metric('Model API attempts', totals['model_calls'], border=True)
            st.metric('Search API attempts', totals['search_calls'], border=True)
            st.metric('Input tokens recorded', f"{totals['input_tokens']:,}", border=True)
            st.metric('Output tokens recorded', f"{totals['output_tokens']:,}", border=True)
        cost_label = 'Known AI cost subtotal' if totals['unpriced_calls'] else 'Estimated AI cost'
        with st.container(horizontal=True, wrap=True):
            st.metric('Input cost recorded', f"${totals['input_cost_usd']:.6f}", border=True)
            st.metric('Output cost recorded', f"${totals['output_cost_usd']:.6f}", border=True)
            st.metric(cost_label, f"${totals['total_cost_usd']:.6f}", border=True)
        if totals['unpriced_calls'] or totals['unknown_usage']:
            st.warning(f"{totals['unknown_usage']} model attempts have unknown token usage; {totals['unpriced_calls']} have unknown cost. Recorded totals are partial, not a complete bill.")
        st.caption('Input cost includes ordinary input, cache reads and cache writes. Cache-write costs are included once, not added again to input. Reasoning is included in output. Retries are included when usage is returned.')
        with st.container(horizontal=True, wrap=True):
            st.metric('Cache-read tokens', f"{totals['cached_input_tokens']:,}", border=True)
            st.metric('Cache-write tokens', f"{totals['cache_write_tokens']:,}", border=True)
            st.metric('Cache-write cost within input', f"${totals['cache_write_cost_usd']:.6f}", border=True)
        st.caption('Cache writes included in complete estimates. Default implicit lifetime: 30 minutes; provider lifetime breakdown takes precedence. Missing counts, unsupported tiers or inconsistent details stay unpriced. Older runs require a new analysis to collect write counts.')
        st.markdown(f'[Model pricing source]({PRICE_SOURCE}) · Snapshot {PRICE_DATE} · Standard text USD; unknown models or unsupported billing tiers remain unpriced.')
        search = [r for r in records if r['provider']=='Tavily']
        credits = sum(r.get('search_credits',0) for r in search)
        unknown = sum('search_credits' not in r for r in search)
        st.caption(f'Tavily: {credits} known basic-search credits; {unknown} attempts with unknown charge. Search costs are separate from AI token costs; your plan/free credits determine the actual bill.')
        st.markdown('[Tavily credits and pricing](https://docs.tavily.com/documentation/api-credits)')
        for agent in ('Discovery','Research','Strategy','Benchmarks'):
            rows = [r for r in records if r['agent']==agent]
            subtotal = summarize(rows)
            with st.expander(f"{agent} · {len(rows)} API attempts · ${subtotal['total_cost_usd']:.6f} known model cost"):
                st.dataframe(rows, hide_index=True)
    st.subheader('Workflow operations')
    st.caption('Local checks, replay steps and provider operations are listed separately from API attempt totals. Events contain no prompts, raw provider responses, credentials or private model reasoning.')
    st.dataframe(result.get('trace',[]), hide_index=True)
    st.caption('Run ID: '+result['run_id'])


def review_panel(result):
    st.subheader('Review & revision')
    count = result.get('revision_count',0)
    st.caption(f'{count} accepted revision cycle · maximum one · automated review does not replace strategist approval.')
    for finding in result.get('review_findings',[]):
        st.write('• '+markdown_text(finding))
    if not result.get('review_findings'):
        st.info('Automated review not available for this draft. Review the evidence manually.')
    st.caption('Review findings are retained as a checklist. A revision is not proof that every concern is resolved.')
    originals = result.get('draft_hypotheses',[])
    finals = result.get('hypotheses',[])
    with st.expander('Inspect original draft and final recommendation'):
        for i, original in enumerate(originals):
            final = finals[i] if i < len(finals) else {}
            st.markdown(f"**Campaign {i+1}**")
            changes = [k for k in original if original[k] != final.get(k)]
            st.caption('Changed fields: '+(', '.join(changes) or 'None'))
            st.json({'original':original, 'final':final}, expanded=False)


def benchmark_panel(result):
    st.subheader('Public acquisition benchmarks')
    research = result.get('benchmarks',{})
    st.write(markdown_text(research.get('limitations','Not available')))
    st.caption('Source-quoted research candidates, not rate cards or forecasts. Amount/quote checks do not establish comparability. Confirm account definition and all cost coverage before adopting a CPA.')
    sources = {s['id']:s for s in result.get('sources',[])}
    for i,b in enumerate(research.get('benchmarks',[]),1):
        with st.container(border=True):
            st.markdown(f"**{i}. {b['channel']} · {markdown_text(b['product'])}**")
            st.write('Reported CPA: '+(f"${b['cpa']:,.2f}" if b['cpa'] is not None else 'Not specified'))
            for key in ('account_definition','geography_audience','period','costs_included','costs_excluded','comparability'):
                st.write(f"{key.replace('_',' ').capitalize()}: {markdown_text(b[key])}")
            st.text('Source quote: '+b['quote'])
            source = sources.get(b['source_id'])
            if source:
                st.link_button('Open benchmark source', source['url'])
                st.caption('Retrieved '+source['retrieved_at'])

