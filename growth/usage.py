"""Session-local provider metadata; no prompts, credentials or raw errors."""
from contextvars import ContextVar
from datetime import datetime, timezone
from time import perf_counter

operation = ContextVar('operation', default=('model:direct', 1))
PRICE_SOURCE = 'https://developers.openai.com/api/docs/pricing'
PRICE_DATE = '2026-10-24'
# Standard text rates USD / million tokens. Unknown models are intentionally unpriced.
RATES = {'gpt-6-luna': (.10, .01, .50), 'gpt-6.1-sol': (2., .10, 10.), 'gpt-6-astra': (10., 1., 50.)}


def role(label):
    prefix = label.split(':')[0]
    return {'discovery':'Discovery', 'search':'Research', 'extract':'Research', 'evidence':'Research', 'analysis':'Strategy', 'strategy':'Strategy', 'benchmarks':'Benchmarks'}.get(prefix, 'System')


def event(provider, model=None):
    label, attempt = operation.get()
    return {'agent':role(label), 'action':label, 'attempt':attempt, 'provider':provider, 'model':model,
            'started_at':datetime.now(timezone.utc).isoformat(), 'outcome':'failed',
            'input_tokens':None, 'output_tokens':None, 'total_tokens':None, 'cached_input_tokens':None,
            'reasoning_tokens':None, 'input_cost_usd':None, 'output_cost_usd':None, 'total_cost_usd':None}


def price_tokens(record, usage, metadata):
    if not isinstance(usage, dict):
        return
    for name in ('input_tokens', 'output_tokens', 'total_tokens'):
        value = usage.get(name)
        record[name] = value if isinstance(value, int) and value >= 0 else None
    details = usage.get('input_token_details') or {}
    cache = details.get('cache_read')
    record['cached_input_tokens'] = cache
    record['reasoning_tokens'] = (usage.get('output_token_details') or {}).get('reasoning')
    # Reasoning is already included in output. Cache reads are a subset of input.
    rates = RATES.get(record['model'])
    tier = metadata.get('service_tier', 'default')
    if not rates or tier not in (None, 'default', 'standard') or any(details.get(k) for k in details if k != 'cache_read'):
        return
    inp, out = record['input_tokens'], record['output_tokens']
    record.update(pricing_source=PRICE_SOURCE,
                  pricing_date=PRICE_DATE, pricing_basis='Standard text USD / million tokens',
                  input_rate=rates[0], cached_input_rate=rates[1], output_rate=rates[2])
    if out is not None:
        record['output_cost_usd'] = out*rates[2]/1e6
    if inp is not None and isinstance(cache, int) and 0 <= cache <= inp:
        record['input_cost_usd'] = ((inp-cache)*rates[0]+cache*rates[1])/1e6
    if record['input_cost_usd'] is not None and record['output_cost_usd'] is not None:
        record['total_cost_usd'] = record['input_cost_usd'] + record['output_cost_usd']


def finish(record, start):
    record['duration_ms'] = round((perf_counter()-start)*1000)


def summarize(records):
    llm = [r for r in records if r['provider']=='OpenAI']
    return {**{k:sum(r.get(k) or 0 for r in llm) for k in ('input_tokens','output_tokens','total_tokens','input_cost_usd','output_cost_usd')},
            'total_cost_usd':sum((r.get('input_cost_usd') or 0)+(r.get('output_cost_usd') or 0) for r in llm),
            'unknown_usage':sum(r.get('total_tokens') is None for r in llm),
            'unpriced_calls':sum(r.get('total_cost_usd') is None for r in llm),
            'model_calls':len(llm), 'search_calls':sum(r['provider']=='Tavily' for r in records)}
