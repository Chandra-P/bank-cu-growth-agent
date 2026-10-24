from __future__ import annotations

import ipaddress
import re
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


class ResearchRequest(BaseModel):
    home: Institution
    market: str = Field(min_length=2, max_length=160)
    product: str = "Consumer checking accounts"

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


class Discovery(BaseModel):
    competitors: list[Institution] = Field(min_length=3, max_length=3)


class Extraction(BaseModel):
    model_config = ConfigDict(extra="ignore")
    facts: dict[str, Fact]
    follow_up: str = Field(default="", max_length=300)


class Analysis(BaseModel):
    hypotheses: list[Hypothesis] = Field(min_length=3, max_length=3)
