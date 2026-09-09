from typing import List, Optional, Literal
from pydantic import BaseModel, Field


# =========================
# REQUEST SCHEMAS
# =========================

class CompetitorRequest(BaseModel):
    companies: List[str] = Field(
        ...,
        min_length=1,
        max_length=10,
        description="List of competitor company or product names to analyze"
    )


# =========================
# UPDATE SCHEMAS
# =========================

class CompetitorUpdate(BaseModel):
    title: str = Field(
        ...,
        description="Short title describing the competitor update"
    )

    category: Literal[
        "product",
        "pricing",
        "hiring",
        "partnership",
        "funding",
        "acquisition",
        "leadership",
        "other"
    ] = Field(
        ...,
        description="Category of the competitor update"
    )

    summary: str = Field(
        ...,
        description="Concise explanation of the update"
    )

    why_it_matters: str = Field(
        ...,
        description="Why this update may be important"
    )

    source: str = Field(
        ...,
        description="URL or name of the source"
    )

    date: Optional[str] = Field(
        default=None,
        description="Date of the update if available"
    )


# =========================
# COMPANY RESULT
# =========================

class CompanyIntelligence(BaseModel):
    company: str

    updates: List[CompetitorUpdate] = Field(
        default_factory=list
    )


# =========================
# RESPONSE SCHEMA
# =========================

class CompetitorResponse(BaseModel):
    companies: List[CompanyIntelligence]

    intelligence_brief: str = Field(
        ...,
        description="Overall concise intelligence summary across all competitors"
    )