from __future__ import annotations

import ipaddress
import re
from typing import Literal
from urllib.parse import urlparse

from pydantic import BaseModel, ConfigDict, Field, field_validator


class Institution(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    domain: str
    reason: str = Field(default="Selected by reviewer", max_length=500)

    @field_validator("name")
    @classmethod
    def clean_name(cls, value):
        value = value.strip()
        if len(value) < 2:
            raise ValueError("Enter an institution name.")
        return value

    @field_validator("domain")
    @classmethod
    def clean_domain(cls, value):
        parsed = urlparse(value.strip() if "://" in value else "https://" + value.strip())
        domain = (parsed.hostname or "").lower().removeprefix("www.")
        if parsed.scheme != "https" or parsed.username or parsed.password or parsed.port:
            raise ValueError("Use a public official HTTPS domain without credentials or a port.")
        try:
            ipaddress.ip_address(domain)
        except ValueError:
            pass
        else:
            raise ValueError("Use an official domain, not an IP address.")
        if not re.fullmatch(r"(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,63}", domain):
            raise ValueError("Enter a public official domain such as example.com.")
        if domain.endswith((".local", ".localhost", ".internal", ".test", ".invalid")):
            raise ValueError("Use a public official domain.")
        return domain


class ClientDiscovery(BaseModel):
    goal: str = Field(default='', max_length=500)
    timeframe: str = Field(default='', max_length=100)
    problem: Literal['Unknown / needs discovery', 'Awareness', 'Application completion', 'Account funding', 'Account activation'] = 'Unknown / needs discovery'
    observation: str = Field(default='', max_length=1000)
    success_definition: str = Field(default='', max_length=500)
    constraints: str = Field(default='', max_length=500)
    confirmed: bool = False

    @field_validator('goal', 'timeframe', 'observation', 'success_definition', 'constraints')
    @classmethod
    def trim_text(cls, value):
        return value.strip()


class ResearchRequest(BaseModel):
    home: Institution
    market: str = Field(min_length=2, max_length=160)
    product: str = "Consumer checking accounts"
    client_brief: str = Field(default="", max_length=2000)
    client_discovery: ClientDiscovery | None = None

    @field_validator("market")
    @classmethod
    def clean_market(cls, value):
        value = value.strip()
        if len(value) < 2:
            raise ValueError("Enter a geographic market.")
        return value


class Source(BaseModel):
    id: str
    title: str = Field(max_length=300)
    url: str
    excerpt: str = Field(max_length=14000)
    retrieved_at: str
    collection: str = "Live Tavily search"


class Fact(BaseModel):
    value: str = Field(default="Not verified", max_length=650)
    source_id: str | None = None
    quote: str | None = Field(default=None, max_length=1000)
    status: str = "Not verified"


FACT_FIELDS = {
    "product_name": "Product",
    "monthly_fee": "Monthly maintenance fee",
    "opening_deposit": "Opening deposit",
    "minimum_balance": "Ongoing balance requirement",
    "fee_waiver": "Fee waiver conditions",
    "acquisition_bonus": "Acquisition offer and conditions",
    "eligibility": "Account / membership eligibility",
    "positioning": "Positioning / core features",
    "recent_news": "Recent news",
}


class Profile(BaseModel):
    institution: Institution
    facts: dict[str, Fact] = Field(default_factory=dict)
    follow_up: str = Field(default="", max_length=300)
    gaps: list[str] = Field(default_factory=list)


class Hypothesis(BaseModel):
    title: str = Field(max_length=180)
    rationale: str = Field(max_length=1000)
    source_ids: list[str] = Field(min_length=1, max_length=8)
    experiment: str = Field(max_length=700)
    success_metric: str = Field(max_length=400)
    caveat: str = Field(max_length=600)
    audience: str = Field(default="To confirm with the client", max_length=350)
    need_connection: str = Field(default="Confirm how this concept addresses the client's priority.", max_length=500)
    message: str = Field(default="Develop using approved product terms.", max_length=350)
    channels: list[Literal["Direct mail", "Display", "Paid social"]] = Field(default_factory=list, max_length=3)
    channel_rationale: str = Field(default="Select channels after client discovery.", max_length=450)
    guardrail: str = Field(default="Confirm product terms and campaign measurement before execution.", max_length=400)
    client_question: str = Field(default="Which client goal or problem should this test address?", max_length=400)


class StrategistTakeaway(BaseModel):
    finding: str = Field(min_length=1, max_length=700)
    implication: str = Field(min_length=1, max_length=700)
    client_question: str = Field(min_length=1, max_length=400)
    source_ids: list[str] = Field(min_length=1, max_length=8)


class Discovery(BaseModel):
    competitors: list[Institution] = Field(min_length=3, max_length=3)


class WebsiteSuggestion(BaseModel):
    institution: Institution
    source_id: str
    quote: str = Field(min_length=3, max_length=500)


class Extraction(BaseModel):
    model_config = ConfigDict(extra="ignore")
    facts: dict[str, Fact]
    follow_up: str = Field(default="", max_length=300)


class Analysis(BaseModel):
    hypotheses: list[Hypothesis] = Field(min_length=3, max_length=3)
    takeaway: StrategistTakeaway | None = None


class Benchmark(BaseModel):
    source_id: str
    quote: str = Field(min_length=1, max_length=1000)
    channel: Literal['Direct mail', 'Display', 'Paid social', 'Blended', 'Unspecified']
    cpa: float | None = Field(default=None, gt=0, allow_inf_nan=False)
    product: str = Field(max_length=200)
    account_definition: str = Field(max_length=300)
    geography_audience: str = Field(max_length=350)
    period: str = Field(max_length=200)
    costs_included: str = Field(max_length=400)
    costs_excluded: str = Field(max_length=400)
    comparability: str = Field(max_length=600)


class BenchmarkResearch(BaseModel):
    benchmarks: list[Benchmark] = Field(default_factory=list, max_length=5)
    limitations: str = Field(max_length=1200)


class RecommendationReview(BaseModel):
    findings: list[str] = Field(min_length=1, max_length=6)
    revision_instructions: str = Field(max_length=1500)
