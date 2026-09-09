import json

from app.services.search_service import SearchService
from app.services.llm_service import LLMService

from app.schemas.competitor import (
    CompetitorRequest,
    CompetitorResponse,
    CompanyIntelligence
)


class CompetitorAgent:

    def __init__(self):
        self.search_service = SearchService()
        self.llm_service = LLMService()


    def _clean_json_response(
        self,
        response_text: str
    ) -> str:
        """
        Removes markdown JSON code fences if the LLM
        returns them despite being instructed not to.
        """

        cleaned_response = response_text.strip()

        if cleaned_response.startswith("```json"):
            cleaned_response = cleaned_response[7:]

        elif cleaned_response.startswith("```"):
            cleaned_response = cleaned_response[3:]

        if cleaned_response.endswith("```"):
            cleaned_response = cleaned_response[:-3]

        return cleaned_response.strip()


    def _create_fallback_response(
        self,
        companies: list[str],
        message: str
    ) -> CompetitorResponse:
        """
        Creates a safe and valid response when the
        analysis process cannot be completed.
        """

        fallback_companies = [
            CompanyIntelligence(
                company=company,
                updates=[]
            )
            for company in companies
        ]

        return CompetitorResponse(
            companies=fallback_companies,
            intelligence_brief=message
        )


    def analyze(
        self,
        request: CompetitorRequest
    ) -> CompetitorResponse:

        # ----------------------------------------
        # STEP 1: SEARCH FOR RECENT UPDATES
        # ----------------------------------------

        try:

            raw_results = (
                self.search_service.search_multiple_companies(
                    companies=request.companies,
                    max_results_per_company=5
                )
            )

        except Exception as e:

            print(
                f"Competitor search error: {str(e)}"
            )

            return self._create_fallback_response(
                companies=request.companies,
                message=(
                    "Unable to search for recent competitor "
                    "updates at this time."
                )
            )


        # ----------------------------------------
        # STEP 2: CLEAN SEARCH RESULTS
        # ----------------------------------------

        cleaned_results = {}

        for company in request.companies:

            results = raw_results.get(
                company,
                []
            )

            cleaned_results[company] = []

            for result in results:

                cleaned_results[company].append(
                    {
                        "title": result.get(
                            "title",
                            ""
                        ),
                        "link": result.get(
                            "link",
                            ""
                        ),
                        "published": result.get(
                            "published",
                            ""
                        )
                    }
                )


        # ----------------------------------------
        # STEP 3: CHECK AVAILABLE RESULTS
        # ----------------------------------------

        total_results = sum(
            len(results)
            for results in cleaned_results.values()
        )

        print(
            f"Total search results sent to LLM: "
            f"{total_results}"
        )

        # Avoid making an unnecessary LLM request
        if total_results == 0:

            return self._create_fallback_response(
                companies=request.companies,
                message=(
                    "No recent search results were found "
                    "for the monitored companies."
                )
            )


        # ----------------------------------------
        # STEP 4: PREPARE LLM CONTEXT
        # ----------------------------------------

        search_context = json.dumps(
            cleaned_results,
            indent=2
        )


        # ----------------------------------------
        # STEP 5: SYSTEM INSTRUCTIONS
        # ----------------------------------------

        system_message = """
You are an AI Competitor Watch Agent.

Your job is to analyze recent competitor information accurately.

Rules:
- Use only the provided search results.
- Never invent information.
- Remove irrelevant news and noise.
- Remove duplicate or near-duplicate updates.
- Preserve source links whenever possible.
- Return only valid JSON.
"""


        # ----------------------------------------
        # STEP 6: BUILD USER PROMPT
        # ----------------------------------------

        prompt = f"""
Analyze the following recent updates about the monitored companies.

Companies being monitored:

{request.companies}

Below are the recent search results:

{search_context}

Your responsibilities:

1. Identify meaningful competitor updates.
2. Remove irrelevant news and noise.
3. Remove duplicate or near-duplicate updates.
4. Categorize every meaningful update into exactly one of:
   - product
   - pricing
   - hiring
   - partnership
   - funding
   - acquisition
   - leadership
   - other
5. Do not invent information.
6. If the search results do not provide enough information,
   do not guess.
7. Use only the information available in the provided search results.
8. Preserve the exact source link from the search results.
9. Provide a concise explanation of why each update matters.

Return ONLY valid JSON in exactly this format:

{{
  "companies": [
    {{
      "company": "Company name",
      "updates": [
        {{
          "title": "Short update title",
          "category": "product",
          "summary": "Concise explanation based only on the provided search result",
          "why_it_matters": "Why this update may be important",
          "source": "Exact source URL from the search results",
          "date": "Date if available, otherwise null"
        }}
      ]
    }}
  ],
  "intelligence_brief": "A concise overall intelligence summary"
}}

Important rules:

- Include every requested company in the "companies" array,
  even if no meaningful updates were found.
- Use an empty "updates" array when nothing meaningful was found.
- Do not create fake source URLs.
- Do not create dates that are not present in the search results.
- Do not invent details that cannot be reasonably determined
  from the provided result titles.
- Return valid JSON only.
- Do not include markdown code blocks.
- Do not include explanations outside the JSON.
"""


        # ----------------------------------------
        # STEP 7: CALL THE LLM
        # ----------------------------------------

        try:

            response_text = self.llm_service.chat(
                messages=[
                    {
                        "role": "system",
                        "content": system_message
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.1
            )

        except Exception as e:

            print(
                f"Competitor LLM error: {str(e)}"
            )

            return self._create_fallback_response(
                companies=request.companies,
                message=(
                    "Recent updates were found, but the AI "
                    "analysis service is currently unavailable."
                )
            )


        # ----------------------------------------
        # STEP 8: CLEAN AND PARSE RESPONSE
        # ----------------------------------------

        try:

            cleaned_response = (
                self._clean_json_response(
                    response_text
                )
            )

            response_data = json.loads(
                cleaned_response
            )

            return CompetitorResponse(
                **response_data
            )

        except Exception as e:

            print(
                f"Competitor agent parsing error: {str(e)}"
            )

            print(
                f"Raw LLM response: {response_text}"
            )

            return self._create_fallback_response(
                companies=request.companies,
                message=(
                    "Recent updates were found, but the AI "
                    "returned an invalid analysis response."
                )
            )