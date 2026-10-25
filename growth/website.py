"""Discovery preflight: a sourced website suggestion, never automatic approval."""
from .evidence import official_url, normalized
from .providers import bounded_call, ProviderError
import re

WEBSITE_EXCLUDED_DOMAINS = ('azurewebsites.net','netlify.app','vercel.app','webflow.io','wixsite.com',
                            'mapquest.com','indeed.com','rocketreach.co','facebook.com','linkedin.com','yelp.com','wikipedia.org')


def public_fi_domain(domain):
    return not any(domain==blocked or domain.endswith('.'+blocked) for blocked in WEBSITE_EXCLUDED_DOMAINS)


def expanded_fi_name(name):
    value=' '.join(name.split())
    value=re.sub(r'\bfcu\b','Federal Credit Union',value,flags=re.IGNORECASE)
    return re.sub(r'\bcu\b','Credit Union',value,flags=re.IGNORECASE)


def grounded_suggestion(suggestion,sources):
    source=next((s for s in sources if s.id==suggestion.source_id),None)
    if source and public_fi_domain(suggestion.institution.domain) and official_url(source.url,suggestion.institution.domain) and normalized(suggestion.quote) in normalized(source.excerpt):
        return {'institution':suggestion.institution.model_dump(),'source':source.model_dump(),'quote':suggestion.quote}
    return None


def resolve_website(search, analyst, name, market, trace):
    if not 2 <= len(name.strip()) <= 120:
        raise ValueError('Enter an FI name')
    search_name=expanded_fi_name(name)
    suggestion=None
    try:
        # Avoid exact-quoting an abbreviation that may not occur on the FI site.
        sources=bounded_call(lambda:search.search(f'"{search_name}" official website checking accounts',exclude_domains=list(WEBSITE_EXCLUDED_DOMAINS)),'discovery:website-search',trace)
        suggestion=bounded_call(lambda:analyst.resolve_website(search_name,market.strip(),sources),'discovery:website-model',trace)
        result=grounded_suggestion(suggestion,sources)
        if result:
            return result
    except (ProviderError,ValueError):
        pass
    trace.append({'agent':'Discovery','action':'discovery:website-recovery','outcome':'Trying one alternative query'})
    # A proposed domain is only a lead. If the primary provider call failed,
    # use an unquoted expanded-name query instead. Never hardcode an FI domain.
    domain=suggestion.institution.domain if suggestion and public_fi_domain(suggestion.institution.domain) else None
    sources=bounded_call(lambda:search.search(f'{search_name} {market.strip()} official website homepage',domain,exclude_domains=list(WEBSITE_EXCLUDED_DOMAINS)),'discovery:website-follow-up-search',trace)
    suggestion=bounded_call(lambda:analyst.resolve_website(search_name,market.strip(),sources),'discovery:website-follow-up-model',trace)
    result=grounded_suggestion(suggestion,sources)
    if not result:
        raise ValueError('Website suggestion could not be grounded')
    return result
