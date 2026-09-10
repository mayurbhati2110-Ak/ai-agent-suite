import json

from app.schemas.lead_qualification import (
    ICP,
    QualifiedLead,
    QualificationReason,
    LeadQualificationData,
    LeadQualificationResponse,
)

from app.services.llm_service import LLMService
from app.services.lead_research_service import LeadResearchService


class LeadQualificationAgent:

    def __init__(self):
        self.llm_service = LLMService()
        self.research_service = LeadResearchService()

    def _parse_json(self, text: str) -> dict:
        """
        Safely parse JSON returned by the LLM.
        Handles markdown code fences as well.
        """

        text = text.strip()

        if text.startswith("```"):
            lines = text.splitlines()

            if lines and lines[0].startswith("```"):
                lines = lines[1:]

            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]

            text = "\n".join(lines).strip()

        try:
            return json.loads(text)

        except json.JSONDecodeError:
            # Try extracting the JSON object from surrounding text
            start = text.find("{")
            end = text.rfind("}")

            if start != -1 and end != -1 and end > start:
                return json.loads(text[start:end + 1])

            raise ValueError("The LLM returned invalid JSON.")

    def _build_unknown_reasons(
        self,
        icp: ICP
    ) -> list[QualificationReason]:
        """
        Safe fallback when the LLM fails.
        Never assumes a criterion is satisfied.
        """

        criteria = []

        # Industry is treated as one ICP dimension
        if icp.target_industries:
            criteria.append(
                "target_industries"
            )

        # Company size is ONE criterion
        if (
            icp.company_size_min is not None
            or icp.company_size_max is not None
        ):
            criteria.append(
                "company_size"
            )

        # Location is treated as one ICP dimension
        if icp.target_locations:
            criteria.append(
                "target_locations"
            )

        # Required technologies are treated as one dimension
        if icp.required_technologies:
            criteria.append(
                "required_technologies"
            )

        # Business model is treated as one dimension
        if icp.target_business_models:
            criteria.append(
                "target_business_models"
            )

        # Additional criteria
        criteria.extend(
            icp.additional_criteria
        )

        return [
            QualificationReason(
                criterion=criterion,
                status="unknown",
                explanation="Insufficient verified information."
            )
            for criterion in criteria
        ]

    def _calculate_score(
        self,
        reasons: list[QualificationReason]
    ) -> int:
        """
        Calculate the lead score deterministically.

        match       = 100% of criterion weight
        partial     = 50%
        not_match   = 0%
        unknown     = 0%

        Every ICP dimension has equal weight.
        """

        if not reasons:
            return 0

        total_points = 0

        for reason in reasons:

            if reason.status == "match":
                total_points += 1

            elif reason.status == "partial":
                total_points += 0.5

        score = (total_points / len(reasons)) * 100

        return round(score)

    def _normalize_fit(
        self,
        score: int
    ) -> str:
        """
        Convert score into a consistent qualification category.
        """

        if score >= 80:
            return "high"

        if score >= 60:
            return "medium"

        return "low"

    def _qualify_single_lead(
        self,
        lead: dict,
        research: dict,
        icp: ICP
    ) -> QualifiedLead:

        system_message = """
You are an AI Lead Qualification Agent.

Your job is to evaluate a company against a predefined Ideal Customer
Profile (ICP).

IMPORTANT RULES:

1. Use ONLY the information provided in the lead data and research.

2. NEVER invent missing information.

3. If information cannot be verified, mark it as "unknown".

4. Every ICP dimension must have exactly ONE reason.

5. Treat the entire company size range (minimum and maximum employees)
   as ONE criterion called "company_size".

6. Clearly distinguish:
   - match
   - partial
   - not_match
   - unknown

7. Do NOT calculate a score.
   The application will calculate the score from your criterion statuses.

8. Do not treat search-result titles alone as confirmed facts unless the
   information is explicitly supported by the provided research.

9. A criterion should be marked "match" only when the available evidence
   supports that the lead satisfies the criterion.

10. If a criterion has multiple acceptable values, such as multiple
    industries, locations, or technologies, evaluate the criterion as
    a whole.

11. Return ONLY valid JSON.
"""

        user_message = f"""
Evaluate this lead against the following ICP.

ICP:
{json.dumps(icp.model_dump(), indent=2)}

LEAD:
{json.dumps(lead, indent=2)}

RESEARCH:
{json.dumps(research, indent=2)}

Evaluate the following ICP dimensions when they are present:

- target_industries
- company_size
- target_locations
- required_technologies
- target_business_models
- additional_criteria

IMPORTANT:

For company_size:

- If employees are known and fall within the minimum and maximum,
  return "match".
- If employees are known but outside the allowed range,
  return "not_match".
- If only part of the range can be evaluated, use "partial" only when
  appropriate.
- If employee information is unavailable, return "unknown".
- Do NOT create separate company_size_min and company_size_max reasons.

For lists such as target_industries, target_locations,
required_technologies, and target_business_models:

- Evaluate the entire list as ONE criterion.
- Do not create one reason for every individual value.

Use these exact criterion names:

- target_industries
- company_size
- target_locations
- required_technologies
- target_business_models
- additional_criteria

Return exactly this JSON structure:

{{
    "reasons": [
        {{
            "criterion": "string",
            "status": "match",
            "explanation": "string"
        }}
    ],
    "known_information": {{
        "field": "verified value"
    }},
    "unknown_information": [
        "missing information"
    ]
}}

Allowed status values:

- match
- partial
- not_match
- unknown

Remember:

Do not invent information.
Do not calculate a score.
Each ICP dimension should appear only once in the reasons list.
"""

        response_text = self.llm_service.chat(
            messages=[
                {
                    "role": "system",
                    "content": system_message
                },
                {
                    "role": "user",
                    "content": user_message
                }
            ],
            temperature=0.1
        )

        result = self._parse_json(
            response_text
        )

        reasons = []

        for reason in result.get(
            "reasons",
            []
        ):

            if not isinstance(
                reason,
                dict
            ):
                continue

            try:
                reasons.append(
                    QualificationReason(
                        criterion=str(
                            reason.get(
                                "criterion",
                                "Unknown criterion"
                            )
                        ),
                        status=reason.get(
                            "status",
                            "unknown"
                        ),
                        explanation=str(
                            reason.get(
                                "explanation",
                                "No explanation provided."
                            )
                        )
                    )
                )

            except Exception:
                continue

        # Python determines the score from the evidence.
        score = self._calculate_score(
            reasons
        )

        known_information = result.get(
            "known_information",
            {}
        )

        if not isinstance(
            known_information,
            dict
        ):
            known_information = {}

        unknown_information = result.get(
            "unknown_information",
            []
        )

        if not isinstance(
            unknown_information,
            list
        ):
            unknown_information = []

        return QualifiedLead(
            company=lead.get(
                "company",
                "Unknown"
            ),
            website=lead.get(
                "website"
            ),
            score=score,
            fit=self._normalize_fit(
                score
            ),
            reasons=reasons,
            known_information=known_information,
            unknown_information=[
                str(item)
                for item in unknown_information
            ],
            research_sources=research.get(
                "sources",
                []
            )
        )

    def analyze(
        self,
        leads: list[dict],
        icp: ICP
    ) -> LeadQualificationResponse:

        if not leads:
            return LeadQualificationResponse(
                success=False,
                summary="No leads were provided.",
                data=LeadQualificationData(
                    total_leads=0,
                    qualified_leads=0,
                    leads=[],
                    top_prospects=[]
                )
            )

        # Step 1: Research leads
        researched_leads = (
            self.research_service.research_leads(
                leads
            )
        )

        qualified_leads = []

        # Step 2: Evaluate each lead
        for item in researched_leads:

            lead = item.get(
                "lead",
                {}
            )

            research = item.get(
                "research",
                {}
            )

            company = lead.get(
                "company",
                "Unknown"
            )

            print(
                f"Qualifying lead: {company}"
            )

            try:

                qualified = (
                    self._qualify_single_lead(
                        lead=lead,
                        research=research,
                        icp=icp
                    )
                )

            except Exception as e:

                print(
                    f"Qualification error for "
                    f"{company}: {str(e)}"
                )

                qualified = QualifiedLead(
                    company=company,
                    website=lead.get(
                        "website"
                    ),
                    score=0,
                    fit="low",
                    reasons=self._build_unknown_reasons(
                        icp
                    ),
                    known_information={
                        key: value
                        for key, value in lead.items()
                        if value not in (
                            None,
                            ""
                        )
                    },
                    unknown_information=[
                        "Lead qualification could not be completed."
                    ],
                    research_sources=research.get(
                        "sources",
                        []
                    )
                )

            qualified_leads.append(
                qualified
            )

        # Step 3: Rank highest scoring leads first
        qualified_leads.sort(
            key=lambda lead: lead.score,
            reverse=True
        )

        # Top 5 prospects
        top_prospects = qualified_leads[:5]

        # A score of 70+ is considered qualified
        qualified_count = sum(
            1
            for lead in qualified_leads
            if lead.score >= 70
        )

        summary = (
            f"Analyzed {len(qualified_leads)} leads. "
            f"{qualified_count} leads met the "
            f"qualification threshold. "
            f"The top prospects were ranked using "
            f"ICP fit and available evidence."
        )

        return LeadQualificationResponse(
            success=True,
            summary=summary,
            data=LeadQualificationData(
                total_leads=len(qualified_leads),
                qualified_leads=qualified_count,
                leads=qualified_leads,
                top_prospects=top_prospects
            )
        )