import re
from urllib.parse import urlparse

from .models import Fact, Institution, Source


def official_url(url: str, domain: str | None = None) -> bool:
    parsed = urlparse(url)
    host = (parsed.hostname or "").lower()
    if parsed.scheme != "https" or parsed.username or parsed.password:
        return False
    return bool(host) and (domain is None or host == domain or host.endswith("." + domain))


def normalized(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip().casefold()


def ground_fact(fact: Fact, sources: list[Source], institution: Institution) -> Fact:
    source = next((s for s in sources if s.id == fact.source_id), None)
    if not source or not official_url(source.url, institution.domain) or not fact.quote or len(fact.quote.strip()) < 3:
        return Fact()
    if normalized(fact.quote) not in normalized(source.excerpt):
        return Fact()
    # A lexical check catches invented amounts. It does not prove semantic entailment.
    numbers = lambda text: set(re.findall(r"\d[\d,]*(?:\.\d+)?", text.replace(",", "")))
    if not numbers(fact.value).issubset(numbers(fact.quote)) or normalized(fact.value) in {"", "not verified", "unknown", "n/a"}:
        return Fact()
    return fact.model_copy(update={"status": "Source-supported"})


def confirm_competitors(home: Institution, competitors: list[Institution]) -> list[Institution]:
    if len(competitors) != 3:
        raise ValueError("Confirm exactly three competitors.")
    domains = [x.domain for x in [home, *competitors]]
    names = [normalized(x.name) for x in [home, *competitors]]
    if len(set(domains)) != 4 or len(set(names)) != 4:
        raise ValueError("Choose three distinct competitors, excluding the home institution.")
    return competitors
