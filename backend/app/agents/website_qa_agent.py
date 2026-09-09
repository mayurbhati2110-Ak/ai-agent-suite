import json

from app.services.website_qa_service import (
    WebsiteQAService
)

from app.services.llm_service import LLMService

from app.schemas.website_qa import (
    WebsiteQARequest,
    WebsiteQAResponse,
    WebsiteQAData,
    QAIssue,
    SEOReport
)


class WebsiteQAAgent:

    def __init__(self):

        self.qa_service = WebsiteQAService()

        self.llm_service = LLMService()


    def _clean_json_response(
        self,
        response_text: str
    ) -> str:

        cleaned = response_text.strip()

        if cleaned.startswith("```json"):
            cleaned = cleaned[7:-3]

        elif cleaned.startswith("```"):
            cleaned = cleaned[3:-3]

        return cleaned.strip()


    def analyze(
        self,
        request: WebsiteQARequest
    ) -> WebsiteQAResponse:

        # -------------------------
        # REAL WEBSITE INSPECTION
        # -------------------------

        website_result = (
            self.qa_service.analyze_website(
                request.url
            )
        )

        confirmed_issues = (
            website_result.get(
                "confirmed_issues",
                []
            )
        )

        page_data = website_result.get(
            "page_data",
            {}
        )

        seo_data = website_result.get(
            "seo_report",
            {}
        )

        # -------------------------
        # LLM ANALYSIS
        # -------------------------

        prompt = f"""
You are an AI Website QA Agent.

Analyze the website information provided below.

IMPORTANT RULES:

1. Do not invent technical problems.
2. The confirmed issues were found through
   automated checks.
3. Your job is to identify only potential
   content, UI or usability issues.
4. These potential observations must be placed
   under suspected_issues.
5. Clearly distinguish confirmed issues from
   subjective or uncertain observations.
6. Use only the provided website content.
7. Return only valid JSON.
8. Do not use markdown code blocks.

Website URL:

{request.url}

Website content:

{page_data.get("text", "")}

Confirmed issues already detected:

{json.dumps(confirmed_issues, indent=2)}

SEO data:

{json.dumps(seo_data, indent=2)}

Return JSON in exactly this format:

{{
    "suspected_issues": [
        {{
            "severity": "low | medium | high",
            "category": "ui | content | usability | seo",
            "page": "{request.url}",
            "issue": "Description of the suspected issue",
            "recommendation": "Suggested improvement"
        }}
    ],
    "priority_actions": [
        "Most important action",
        "Second important action"
    ],
    "summary": "Concise overall QA summary"
}}

If there are no meaningful suspected issues,
return an empty array.

Never present suspected issues as confirmed.
"""

        try:

            response_text = (
                self.llm_service.chat(
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "You are a careful website "
                                "quality assurance analyst."
                            )
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    temperature=0.1
                )
            )

            cleaned_response = (
                self._clean_json_response(
                    response_text
                )
            )

            llm_result = json.loads(
                cleaned_response
            )

        except Exception as e:

            print(
                f"Website QA LLM error: {str(e)}"
            )

            llm_result = {
                "suspected_issues": [],
                "priority_actions": [],
                "summary": (
                    "Website inspection completed, "
                    "but AI analysis could not be "
                    "completed."
                )
            }

        # -------------------------
        # BUILD RESPONSE
        # -------------------------

        confirmed_models = [
            QAIssue(**issue)
            for issue in confirmed_issues
        ]

        suspected_models = [
            QAIssue(**issue)
            for issue in llm_result.get(
                "suspected_issues",
                []
            )
        ]

        seo_report = SEOReport(
            title=seo_data.get("title"),
            meta_description=seo_data.get(
                "meta_description"
            ),
            h1_count=seo_data.get("h1_count")
        )

        data = WebsiteQAData(
            confirmed_issues=confirmed_models,
            suspected_issues=suspected_models,
            seo_report=seo_report,
            priority_actions=llm_result.get(
                "priority_actions",
                []
            )
        )

        return WebsiteQAResponse(
            success=True,
            url=request.url,
            summary=llm_result.get(
                "summary",
                "Website QA analysis completed."
            ),
            data=data
        )