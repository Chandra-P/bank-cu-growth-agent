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
            'cache_write_tokens':None, 'cache_write_30m_tokens':None, 'cache_write_12h_tokens':None,
            'ordinary_input_tokens':None, 'reasoning_tokens':None, 'input_cost_usd':None,
            'ordinary_input_cost_usd':None, 'cache_read_cost_usd':None, 'cache_write_cost_usd':None,
            'output_cost_usd':None, 'total_cost_usd':None, 'pricing_status':'Usage unavailable'}


def price_tokens(record, usage, metadata):
    if not isinstance(usage, dict):
        return
    valid = lambda value: type(value) is int and value >= 0
    for name in ('input_tokens', 'output_tokens', 'total_tokens'):
        value = usage.get(name)
        record[name] = value if valid(value) else None
    details = usage.get('input_token_details') or {}
    raw = (metadata.get('token_usage') or {}).get('prompt_tokens_details') or {}
    if not raw:
        raw = (metadata.get('token_usage') or {}).get('input_tokens_details') or {}
    cache = details.get('cache_read')
    writes = details.get('cache_creation', raw.get('cache_write_tokens'))
    record['cached_input_tokens'] = cache if valid(cache) else None
    record['cache_write_tokens'] = writes if valid(writes) else None
    reasoning = (usage.get('output_token_details') or {}).get('reasoning')
    record['reasoning_tokens'] = reasoning if valid(reasoning) else None
    record['service_tier'] = metadata.get('service_tier', 'default')
    # Read/write counts partition input; reasoning is already included in output.
    rates = RATES.get(record['model'])
    if not rates or record['service_tier'] not in (None, 'default', 'standard'):
        record['pricing_status'] = 'Unknown model pricing or unsupported service tier'
        return
    if any(details.get(k) for k in details if k not in ('cache_read','cache_creation')) or any(v for k,v in (usage.get('output_token_details') or {}).items() if k != 'reasoning'):
        record['pricing_status'] = 'Unsupported token modality or billing details'
        return
    inp, out = record['input_tokens'], record['output_tokens']
    record.update(pricing_source=PRICE_SOURCE,
                  pricing_date=PRICE_DATE, pricing_basis='Standard text USD / million tokens',
                  input_rate=rates[0], cached_input_rate=rates[1], output_rate=rates[2],
                  cache_write_30m_rate=rates[0]*1.25, cache_write_12h_rate=rates[0]*2.5,
                  cache_pricing_source='https://developers.openai.com/api/docs/guides/prompt-caching')
    if out is not None:
        record['output_cost_usd'] = out*rates[2]/1e6
    if inp is None or not valid(cache) or not valid(writes) or cache+writes > inp:
        record['pricing_status'] = 'Missing or invalid cache read/write token partition'
        return
    if any(k in raw and raw[k] != v for k,v in [('cached_tokens',cache),('cache_write_tokens',writes)]):
        record['pricing_status'] = 'Conflicting provider cache token counts'
        return
    lifetime = raw.get('cache_write_tokens_details')
    if lifetime is not None:
        short, long = lifetime.get('ttl_30m_tokens'), lifetime.get('ttl_12h_tokens')
        if not valid(short) or not valid(long) or short+long != writes:
            record['pricing_status'] = 'Invalid cache-write lifetime breakdown'
            return
        basis = 'Provider-reported lifetime breakdown'
    else:
        # This app uses implicit caching with no request/breakpoint TTL overrides.
        # OpenAI documents 30m as the default for these models.
        short, long = writes, 0
        basis = 'Default 30m; app sends no lifetime overrides'
    record.update(ordinary_input_tokens=inp-cache-writes, cache_write_30m_tokens=short,
                  cache_write_12h_tokens=long, cache_write_lifetime_basis=basis,
                  ordinary_input_cost_usd=(inp-cache-writes)*rates[0]/1e6,
                  cache_read_cost_usd=cache*rates[1]/1e6,
                  cache_write_cost_usd=(short*rates[0]*1.25+long*rates[0]*2.5)/1e6)
    record['input_cost_usd'] = sum(record[k] for k in ('ordinary_input_cost_usd','cache_read_cost_usd','cache_write_cost_usd'))
    if record['input_cost_usd'] is not None and record['output_cost_usd'] is not None:
        record['total_cost_usd'] = record['input_cost_usd'] + record['output_cost_usd']
        record['pricing_status'] = 'Complete estimate'
    else:
        record['pricing_status'] = 'Output usage unavailable'


def finish(record, start):
    record['duration_ms'] = round((perf_counter()-start)*1000)


def summarize(records):
    llm = [r for r in records if r['provider']=='OpenAI']
    return {**{k:sum(r.get(k) or 0 for r in llm) for k in ('input_tokens','output_tokens','total_tokens','input_cost_usd','output_cost_usd','cached_input_tokens','cache_write_tokens','cache_write_cost_usd')},
            'total_cost_usd':sum((r.get('input_cost_usd') or 0)+(r.get('output_cost_usd') or 0) for r in llm),
            'unknown_usage':sum(r.get('total_tokens') is None for r in llm),
            'unpriced_calls':sum(r.get('total_cost_usd') is None for r in llm),
            'model_calls':len(llm), 'search_calls':sum(r['provider']=='Tavily' for r in records)}
