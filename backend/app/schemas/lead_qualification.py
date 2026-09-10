from typing import List, Optional, Literal
from pydantic import BaseModel, Field


# =========================
# ICP SCHEMA
# =========================

class ICP(BaseModel):
    """
    Ideal Customer Profile used to evaluate leads.
    """

    target_industries: List[str] = Field(
        default_factory=list,
        description="Industries that are a good fit"
    )

    company_size_min: Optional[int] = Field(
        default=None,
        description="Minimum number of employees"
    )

    company_size_max: Optional[int] = Field(
        default=None,
        description="Maximum number of employees"
    )

    target_locations: List[str] = Field(
        default_factory=list,
        description="Target countries, regions or cities"
    )

    required_technologies: List[str] = Field(
        default_factory=list,
        description="Technologies that indicate a good fit"
    )

    target_business_models: List[str] = Field(
        default_factory=list,
        description="Target business models"
    )

    additional_criteria: List[str] = Field(
        default_factory=list,
        description="Additional qualification criteria"
    )


# =========================
# LEAD DATA
# =========================

class Lead(BaseModel):
    """
    A single lead extracted from the uploaded CSV.
    """

    company: str = Field(
        ...,
        description="Company name"
    )

    website: Optional[str] = Field(
        default=None,
        description="Company website"
    )

    industry: Optional[str] = Field(
        default=None,
        description="Industry from CSV if available"
    )

    employees: Optional[int] = Field(
        default=None,
        description="Number of employees if available"
    )

    location: Optional[str] = Field(
        default=None,
        description="Company location"
    )

    contact_name: Optional[str] = Field(
        default=None,
        description="Lead contact name"
    )

    contact_email: Optional[str] = Field(
        default=None,
        description="Lead contact email"
    )

    additional_data: dict = Field(
        default_factory=dict,
        description="Any additional CSV fields"
    )


# =========================
# QUALIFICATION RESULT
# =========================

class QualificationReason(BaseModel):
    """
    Explanation for an individual qualification criterion.
    """

    criterion: str = Field(
        ...,
        description="ICP criterion being evaluated"
    )

    status: Literal[
        "match",
        "partial",
        "not_match",
        "unknown"
    ] = Field(
        ...,
        description="Qualification status"
    )

    explanation: str = Field(
        ...,
        description="Evidence-based explanation"
    )


class QualifiedLead(BaseModel):
    """
    Final qualification result for one lead.
    """

    company: str

    website: Optional[str] = None

    score: int = Field(
        ...,
        ge=0,
        le=100,
        description="Lead qualification score from 0 to 100"
    )

    fit: Literal[
        "high",
        "medium",
        "low"
    ]

    reasons: List[QualificationReason] = Field(
        default_factory=list
    )

    known_information: dict = Field(
        default_factory=dict
    )

    unknown_information: List[str] = Field(
        default_factory=list,
        description="Information that could not be verified"
    )

    research_sources: List[str] = Field(
        default_factory=list,
        description="Sources used during enrichment"
    )


# =========================
# REQUEST SCHEMA
# =========================

class LeadQualificationRequest(BaseModel):
    """
    Request configuration for lead qualification.
    """

    icp: ICP = Field(
        ...,
        description="Ideal Customer Profile"
    )


# =========================
# RESPONSE DATA
# =========================

class LeadQualificationData(BaseModel):

    total_leads: int

    qualified_leads: int

    leads: List[QualifiedLead] = Field(
        default_factory=list
    )

    top_prospects: List[QualifiedLead] = Field(
        default_factory=list
    )


# =========================
# RESPONSE SCHEMA
# =========================

class LeadQualificationResponse(BaseModel):

    success: bool

    summary: str

    data: LeadQualificationData