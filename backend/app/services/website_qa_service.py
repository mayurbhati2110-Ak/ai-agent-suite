import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse


class WebsiteQAService:

    def __init__(self):
        self.timeout = 10
        self.max_links = 30

        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 "
                "(Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 "
                "Chrome/120 Safari/537.36"
            )
        }

    def normalize_url(self, url: str) -> str:
        """
        Normalize user-entered URLs.

        Examples:
        example.com -> https://example.com
        www.example.com -> https://www.example.com
        http://example.com -> http://example.com
        https://example.com -> https://example.com
        """

        url = url.strip()

        if not url:
            raise ValueError("Website URL cannot be empty.")

        parsed = urlparse(url)

        if not parsed.scheme:
            url = f"https://{url}"

        return url


    def analyze_website(self, url: str) -> dict:

        # Normalize URL before making requests
        url = self.normalize_url(url)

        result = {
            "url": url,
            "confirmed_issues": [],
            "page_data": {},
            "seo_report": {}
        }

        try:

            response = requests.get(
                url,
                headers=self.headers,
                timeout=self.timeout
            )

            result["page_data"]["status_code"] = response.status_code

            if response.status_code >= 400:

                result["confirmed_issues"].append(
                    {
                        "severity": "high",
                        "category": "accessibility",
                        "page": url,
                        "issue": (
                            f"Website returned HTTP "
                            f"{response.status_code}"
                        ),
                        "recommendation": (
                            "Check server availability and "
                            "fix the HTTP error."
                        )
                    }
                )

                return result

            soup = BeautifulSoup(
                response.text,
                "html.parser"
            )

            # -------------------------
            # TITLE CHECK
            # -------------------------

            title = soup.title

            if not title or not title.get_text(strip=True):

                result["confirmed_issues"].append(
                    {
                        "severity": "medium",
                        "category": "seo",
                        "page": url,
                        "issue": "Missing page title",
                        "recommendation": (
                            "Add a descriptive and unique "
                            "<title> tag."
                        )
                    }
                )

            else:

                result["seo_report"]["title"] = (
                    title.get_text(strip=True)
                )

            # -------------------------
            # META DESCRIPTION CHECK
            # -------------------------

            meta_description = soup.find(
                "meta",
                attrs={"name": "description"}
            )

            if (
                not meta_description
                or not meta_description.get("content")
            ):

                result["confirmed_issues"].append(
                    {
                        "severity": "medium",
                        "category": "seo",
                        "page": url,
                        "issue": "Missing meta description",
                        "recommendation": (
                            "Add a concise meta description "
                            "for search engines."
                        )
                    }
                )

            else:

                result["seo_report"]["meta_description"] = (
                    meta_description.get("content")
                )

            # -------------------------
            # H1 CHECK
            # -------------------------

            h1_tags = soup.find_all("h1")

            result["seo_report"]["h1_count"] = len(
                h1_tags
            )

            if len(h1_tags) == 0:

                result["confirmed_issues"].append(
                    {
                        "severity": "medium",
                        "category": "seo",
                        "page": url,
                        "issue": "No H1 heading found",
                        "recommendation": (
                            "Add a clear primary H1 heading."
                        )
                    }
                )

            # -------------------------
            # IMAGE CHECK
            # -------------------------

            images = soup.find_all("img")

            result["page_data"]["image_count"] = len(
                images
            )

            for image in images[:20]:

                image_src = image.get("src")

                if not image_src:

                    result["confirmed_issues"].append(
                        {
                            "severity": "medium",
                            "category": "missing_image",
                            "page": url,
                            "issue": (
                                "Image element is missing "
                                "a source URL"
                            ),
                            "recommendation": (
                                "Provide a valid image source."
                            )
                        }
                    )

                    continue

                image_url = urljoin(
                    url,
                    image_src
                )

                try:

                    image_response = requests.get(
                        image_url,
                        headers=self.headers,
                        timeout=5
                    )

                    if image_response.status_code >= 400:

                        result[
                            "confirmed_issues"
                        ].append(
                            {
                                "severity": "medium",
                                "category": "missing_image",
                                "page": url,
                                "issue": (
                                    f"Image returned HTTP "
                                    f"{image_response.status_code}: "
                                    f"{image_url}"
                                ),
                                "recommendation": (
                                    "Fix or replace the broken "
                                    "image URL."
                                )
                            }
                        )

                except requests.RequestException:

                    result[
                        "confirmed_issues"
                    ].append(
                        {
                            "severity": "medium",
                            "category": "missing_image",
                            "page": url,
                            "issue": (
                                f"Image could not be loaded: "
                                f"{image_url}"
                            ),
                            "recommendation": (
                                "Verify that the image is "
                                "available."
                            )
                        }
                    )

            # -------------------------
            # LINK CHECK
            # -------------------------

            links = soup.find_all("a")

            checked_links = set()

            for link in links:

                href = link.get("href")

                if not href:
                    continue

                if href.startswith("#"):
                    continue

                if href.startswith(
                    ("mailto:", "tel:", "javascript:")
                ):
                    continue

                full_url = urljoin(
                    url,
                    href
                )

                if full_url in checked_links:
                    continue

                checked_links.add(full_url)

                if len(checked_links) > self.max_links:
                    break

                parsed = urlparse(full_url)

                if parsed.scheme not in (
                    "http",
                    "https"
                ):
                    continue

                try:

                    link_response = requests.get(
                        full_url,
                        headers=self.headers,
                        timeout=5,
                        allow_redirects=True
                    )

                    if link_response.status_code >= 400:

                        result[
                            "confirmed_issues"
                        ].append(
                            {
                                "severity": "high",
                                "category": "broken_link",
                                "page": url,
                                "issue": (
                                    f"Broken link returns "
                                    f"HTTP "
                                    f"{link_response.status_code}: "
                                    f"{full_url}"
                                ),
                                "recommendation": (
                                    "Update, fix or remove "
                                    "the broken link."
                                )
                            }
                        )

                except requests.RequestException:

                    result[
                        "confirmed_issues"
                    ].append(
                        {
                            "severity": "high",
                            "category": "broken_link",
                            "page": url,
                            "issue": (
                                f"Link could not be reached: "
                                f"{full_url}"
                            ),
                            "recommendation": (
                                "Verify the destination URL."
                            )
                        }
                    )

            # -------------------------
            # PAGE CONTENT
            # -------------------------

            result["page_data"]["text"] = (
                soup.get_text(
                    " ",
                    strip=True
                )[:8000]
            )

            result["page_data"]["link_count"] = len(
                checked_links
            )

            return result

        except requests.RequestException as e:

            result["confirmed_issues"].append(
                {
                    "severity": "high",
                    "category": "accessibility",
                    "page": url,
                    "issue": (
                        f"Website could not be accessed: "
                        f"{str(e)}"
                    ),
                    "recommendation": (
                        "Check the URL and website "
                        "availability."
                    )
                }
            )

            return result