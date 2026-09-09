import feedparser
from urllib.parse import quote


class SearchService:

    @staticmethod
    def search_company(company: str, max_results: int = 10) -> list[dict]:
        """
        Searches Google News for recent updates about a company.

        Returns raw search results that will later be filtered
        and analyzed by the CompetitorAgent.
        """

        query = f'"{company}"'

        url = (
            "https://news.google.com/rss/search?"
            f"q={quote(query)}&hl=en-US&gl=US&ceid=US:en"
        )

        try:
            feed = feedparser.parse(url)

            results = []

            for entry in feed.entries[:max_results]:

                results.append(
                    {
                        "title": entry.get("title", ""),
                        "link": entry.get("link", ""),
                        "published": entry.get("published", ""),
                        "summary": entry.get("summary", "")
                    }
                )

            return results

        except Exception as e:
            print(f"Search error for {company}: {str(e)}")

            return []

    @staticmethod
    def search_multiple_companies(
        companies: list[str],
        max_results_per_company: int = 10
    ) -> dict[str, list[dict]]:
        """
        Searches recent updates for multiple companies.
        """

        all_results = {}

        for company in companies:

            print(f"Searching recent updates for: {company}")

            results = SearchService.search_company(
                company=company,
                max_results=max_results_per_company
            )

            all_results[company] = results

        return all_results