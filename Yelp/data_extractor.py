"""
Data extraction module for Yelp and Google search
"""

import requests
import re
from config import SERPER_API_KEY, INSTAGRAM_SEARCH_NUM


class DataExtractor:
    """Handles data extraction from various sources"""

    SEARCH_QUERIES = [
        "barbershops in Boston Massachusetts",
        "barber shop Boston MA",
        "men's haircut Boston",
        "barbershop downtown Boston",
        "barbershop Cambridge MA",
        "barbershop Back Bay Boston",
        "barbershop South Boston",
        "barbershop North End Boston",
        "barbershop Beacon Hill Boston",
        "barbershop Fenway Boston",
        "barbershop Dorchester Boston",
        "barbershop Allston Boston",
        "barbershop Brighton Boston",
        "barbershop West End Boston",
        "barbershop Roxbury Boston",
        "barbershop Jamaica Plain Boston",
        "barbershop South End Boston",
        "barbershop Brookline MA",
        "barbershop Somerville MA",
        "barbershop Watertown MA"
    ]

    @staticmethod
    def get_yelp_businesses():
        """Extract Yelp business data using Serper API"""

        url = "https://google.serper.dev/search"

        headers = {
            "X-API-KEY": SERPER_API_KEY,
            "Content-Type": "application/json"
        }

        businesses = []
        seen_urls = set()  # prevents duplicates

        try:

            for query in DataExtractor.SEARCH_QUERIES:

                print(f"Searching: {query}")

                for start in range(0, 5, 10):

                    payload = {
                        "q": f"{query} site:yelp.com/biz",
                        "num": 10,
                        "start": start
                    }

                    r = requests.post(url, json=payload, headers=headers)
                    data = r.json()

                    for result in data.get("organic", []):

                        link = result.get("link")

                        if not link or "yelp.com/biz" not in link:
                            continue

                        # Remove duplicates
                        if link in seen_urls:
                            continue

                        seen_urls.add(link)

                        business = DataExtractor._parse_yelp_result(result)

                        businesses.append(business)

            print(f"Total unique businesses found: {len(businesses)}")

            return businesses

        except Exception as e:
            print(f"Error extracting Yelp data: {e}")
            return []

    @staticmethod
    def _parse_yelp_result(result):
        """Parse individual Yelp result"""

        name = result.get("title", "") \
            .replace(" Photos - Yelp", "") \
            .replace(" - Updated March 2026 - Yelp", "") \
            .replace(" - Boston, Massachusetts - Yelp", "") \
            .replace(" - Yelp", "") \
            .strip()

        rating = result.get("rating")
        reviews = result.get("ratingCount")
        snippet = result.get("snippet", "")
        link = result.get("link")

        # Extract phone
        phone = None
        if "(" in snippet and ")" in snippet:
            start = snippet.find("(")
            end = snippet.find(")", start) + 8
            if end <= len(snippet):
                phone = snippet[start:end].strip()

        # Use full snippet as address
        address = snippet

        return {
            "Name": name,
            "Rating": rating,
            "Reviews": reviews,
            "Phone": phone,
            "Address": address,
            "Yelp URL": link
        }

    @staticmethod
    def find_instagram(business_name):
        """Find Instagram account for a business"""

        try:

            query = f"{business_name} barbershop Boston Instagram"

            url = "https://google.serper.dev/search"

            payload = {
                "q": query,
                "num": INSTAGRAM_SEARCH_NUM
            }

            headers = {
                "X-API-KEY": SERPER_API_KEY,
                "Content-Type": "application/json"
            }

            r = requests.post(url, json=payload, headers=headers)
            data = r.json()

            for result in data.get("organic", []):

                link = result.get("link", "")

                if "instagram.com" in link:
                    print(f"Found Instagram for {business_name}: {link}")
                    return link

        except Exception as e:
            print(f"Error finding Instagram: {e}")

        return None