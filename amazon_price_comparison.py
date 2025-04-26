import aiohttp
import asyncio
from bs4 import BeautifulSoup
import json
from typing import Dict, Optional
import time
from urllib.parse import quote_plus
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse


class AmazonPriceComparer:
    def __init__(self):
        self.countries = {
            "US": {
                "domain": "amazon.com",
                "currency": "USD",
                "headers": {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
                },
            },
            "UK": {
                "domain": "amazon.co.uk",
                "currency": "GBP",
                "headers": {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
                },
            },
            "DE": {
                "domain": "amazon.de",
                "currency": "EUR",
                "headers": {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
                },
            },
            "FR": {
                "domain": "amazon.fr",
                "currency": "EUR",
                "headers": {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
                },
            },
            "IT": {
                "domain": "amazon.it",
                "currency": "EUR",
                "headers": {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
                },
            },
            "ES": {
                "domain": "amazon.es",
                "currency": "EUR",
                "headers": {
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
                },
            },
        }
        self.timeout = aiohttp.ClientTimeout(total=10)  # 10 seconds timeout

    async def _fetch_price(
        self,
        session: aiohttp.ClientSession,
        country: str,
        config: dict,
        url: str,
        product_id: str = None,
    ) -> tuple:
        try:
            async with session.get(url, headers=config["headers"]) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, "html.parser")
                    price_element = soup.find("span", {"class": "a-price-whole"})
                    if price_element:
                        price_text = price_element.text.strip().replace(",", "")
                        price = float(price_text)
                        # Add product URL
                        if product_id:
                            product_url = (
                                f"https://www.{config['domain']}/dp/{product_id}"
                            )
                        else:
                            # Try to get the first product's ASIN from the search results
                            link = soup.find(
                                "a", {"class": "a-link-normal", "href": True}
                            )
                            if link and "/dp/" in link["href"]:
                                asin = link["href"].split("/dp/")[1].split("/")[0]
                                product_url = (
                                    f"https://www.{config['domain']}/dp/{asin}"
                                )
                            else:
                                product_url = url
                        return country, {
                            "price": price,
                            "currency": config["currency"],
                            "url": product_url,
                        }
                return country, None
        except Exception as e:
            print(f"Error searching {country}: {str(e)}")
            return country, None

    async def search_by_product_id(self, product_id: str) -> Dict[str, Optional[float]]:
        """
        Search for a product by its Amazon product ID (ASIN/DP) across different Amazon domains
        """
        results = {}
        async with aiohttp.ClientSession(timeout=self.timeout) as session:
            tasks = []
            for country, config in self.countries.items():
                product_url = f"https://www.{config['domain']}/dp/{product_id}"
                tasks.append(
                    self._fetch_price(
                        session, country, config, product_url, product_id=product_id
                    )
                )

            # Wait for all requests to complete
            completed_tasks = await asyncio.gather(*tasks)

            # Process results
            for country, result in completed_tasks:
                results[country] = result

        return results

    async def search_product(self, product_name: str) -> Dict[str, Optional[float]]:
        """
        Search for a product across different Amazon domains and return prices
        """
        results = {}
        async with aiohttp.ClientSession(timeout=self.timeout) as session:
            tasks = []
            for country, config in self.countries.items():
                search_url = (
                    f"https://www.{config['domain']}/s?k={quote_plus(product_name)}"
                )
                tasks.append(self._fetch_price(session, country, config, search_url))

            # Wait for all requests to complete
            completed_tasks = await asyncio.gather(*tasks)

            # Process results
            for country, result in completed_tasks:
                results[country] = result

        return results


async def main():
    comparer = AmazonPriceComparer()

    while True:
        print("\nChoose search method:")
        print("1. Search by product name")
        print("2. Search by product ID (ASIN/DP)")
        print("3. Quit")

        choice = input("\nEnter your choice (1-3): ")

        if choice == "3":
            break
        elif choice == "1":
            product_name = input("\nEnter product name to search: ")
            print(f"\nSearching for '{product_name}' across Amazon domains...")
            results = await comparer.search_product(product_name)
        elif choice == "2":
            product_id = input("\nEnter Amazon product ID (ASIN/DP): ")
            print(f"\nSearching for product ID '{product_id}' across Amazon domains...")
            results = await comparer.search_by_product_id(product_id)
        else:
            print("Invalid choice. Please try again.")
            continue

        print("\nResults:")
        print("=" * 80)
        for country, data in results.items():
            if data:
                print(f"\n{country}:")
                print(f"  Price: {data['price']} {data['currency']}")
                print(f"  URL: {data['url']}")
                print(f"  Preview: Open in browser to view product")
                print("-" * 40)
            else:
                print(f"\n{country}: Not found or error occurred")
                print("-" * 40)
        print("=" * 80)

        # Ask if user wants to open any URLs
        while True:
            open_url = input(
                "\nWould you like to open any product URLs? (y/n): "
            ).lower()
            if open_url == "n":
                break
            elif open_url == "y":
                country = input("Enter country code (e.g., US, UK, DE): ").upper()
                if country in results and results[country]:
                    import webbrowser

                    webbrowser.open(results[country]["url"])
                    print(f"Opening {country} product page...")
                else:
                    print("Invalid country code or no data available for that country.")
            else:
                print("Please enter 'y' or 'n'.")


if __name__ == "__main__":
    asyncio.run(main())
