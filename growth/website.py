"""Discovery preflight: a sourced website suggestion, never automatic approval."""
from .evidence import official_url, normalized
from .providers import bounded_call


def resolve_website(search, analyst, name, market, trace):
    if not 2 <= len(name.strip()) <= 120:
        raise ValueError('Enter an FI name')
    # Location-heavy queries can return directories instead of the FI itself.
    sources=bounded_call(lambda:search.search(f'"{name.strip()}" official website checking accounts'), 'discovery:website-search',trace)
    suggestion=bounded_call(lambda:analyst.resolve_website(name.strip(),market.strip(),sources),'discovery:website-model',trace)
    source=next((s for s in sources if s.id==suggestion.source_id),None)
    if not source or not official_url(source.url,suggestion.institution.domain) or normalized(suggestion.quote) not in normalized(source.excerpt):
        # A guessed domain is only a search lead. Require an on-domain source
        # and a new grounded identity suggestion before presenting it.
        sources=bounded_call(lambda:search.search(f'"{name.strip()}" official website {market.strip()}',suggestion.institution.domain),'discovery:website-follow-up-search',trace)
        suggestion=bounded_call(lambda:analyst.resolve_website(name.strip(),market.strip(),sources),'discovery:website-follow-up-model',trace)
        source=next((s for s in sources if s.id==suggestion.source_id),None)
    if not source or not official_url(source.url,suggestion.institution.domain) or normalized(suggestion.quote) not in normalized(source.excerpt):
        raise ValueError('Website suggestion could not be grounded')
    return {'institution':suggestion.institution.model_dump(),'source':source.model_dump(),'quote':suggestion.quote}
