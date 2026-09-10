import requests
from bs4 import BeautifulSoup
from urllib.parse import quote


class LeadResearchService:

    def __init__(self):
        self.timeout = 10

        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 "
                "(Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 "
                "Chrome/120 Safari/537.36"
            )
        }

    # ----------------------------------------
    # SEARCH COMPANY
    # ----------------------------------------

    def search_company(
        self,
        company: str,
        max_results: int = 5
    ) -> list[dict]:

        query = quote(f'"{company}" company')

        url = (
            "https://www.google.com/search?"
            f"q={query}"
        )

        try:

            response = requests.get(
                url,
                headers=self.headers,
                timeout=self.timeout
            )

            response.raise_for_status()

            soup = BeautifulSoup(
                response.text,
                "html.parser"
            )

            results = []

            for result in soup.select("div.MjjYud"):

                link = result.find("a")
                heading = result.find(["h3"])

                if not link or not heading:
                    continue

                href = link.get("href")

                if not href:
                    continue

                results.append(
                    {
                        "title": heading.get_text(
                            " ",
                            strip=True
                        ),
                        "link": href
                    }
                )

                if len(results) >= max_results:
                    break

            return results

        except Exception as e:

            print(
                f"Lead research search error "
                f"for {company}: {str(e)}"
            )

            return []

    # ----------------------------------------
    # FETCH WEBSITE
    # ----------------------------------------

    def fetch_website(
        self,
        website: str
    ) -> dict:

        if not website:
            return {}

        try:

            response = requests.get(
                website,
                headers=self.headers,
                timeout=self.timeout
            )

            response.raise_for_status()

            soup = BeautifulSoup(
                response.text,
                "html.parser"
            )

            title = soup.title

            description = soup.find(
                "meta",
                attrs={"name": "description"}
            )

            return {
                "url": website,
                "title": (
                    title.get_text(
                        " ",
                        strip=True
                    )
                    if title
                    else None
                ),
                "description": (
                    description.get("content")
                    if description
                    else None
                ),
                "text": soup.get_text(
                    " ",
                    strip=True
                )[:8000]
            }

        except Exception as e:

            print(
                f"Website research error "
                f"for {website}: {str(e)}"
            )

            return {}

    # ----------------------------------------
    # RESEARCH ONE LEAD
    # ----------------------------------------

    def research_lead(
        self,
        company: str,
        website: str | None = None
    ) -> dict:

        research = {
            "company": company,
            "search_results": [],
            "website_data": {},
            "sources": []
        }

        # Search company
        search_results = self.search_company(
            company=company,
            max_results=5
        )

        research["search_results"] = search_results

        for result in search_results:

            link = result.get("link")

            if link:
                research["sources"].append(
                    link
                )

        # Research website if supplied
        if website:

            website_data = self.fetch_website(
                website
            )

            research["website_data"] = website_data

            if website_data.get("url"):
                research["sources"].append(
                    website_data["url"]
                )

        return research

    # ----------------------------------------
    # RESEARCH MULTIPLE LEADS
    # ----------------------------------------

    def research_leads(
        self,
        leads: list[dict]
    ) -> list[dict]:

        results = []

        for lead in leads:

            company = lead.get(
                "company",
                ""
            )

            website = lead.get(
                "website"
            )

            if not company:
                continue

            print(
                f"Researching lead: {company}"
            )

            research = self.research_lead(
                company=company,
                website=website
            )

            results.append(
                {
                    "lead": lead,
                    "research": research
                }
            )

        return results