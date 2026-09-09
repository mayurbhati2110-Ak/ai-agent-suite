from pydantic import BaseModel, Field
from typing import List, Optional


class WebsiteQARequest(BaseModel):

    url: str = Field(
        ...,
        description="Website URL to analyze"
    )


class QAIssue(BaseModel):

    severity: str
    category: str

    page: Optional[str] = None

    issue: str

    recommendation: str


class SEOReport(BaseModel):

    title: Optional[str] = None

    meta_description: Optional[str] = None

    h1_count: Optional[int] = None


class WebsiteQAData(BaseModel):

    confirmed_issues: List[QAIssue]

    suspected_issues: List[QAIssue]

    seo_report: SEOReport

    priority_actions: List[str]


class WebsiteQAResponse(BaseModel):

    success: bool

    url: str

    summary: str

    data: WebsiteQAData