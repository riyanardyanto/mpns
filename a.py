import json
from pprint import pprint

import httpx
import spa_scraper


def test_get_spa_data():
    # Mock the HTTPX client
    mock_client = httpx.Client()

    url = "http://127.0.0.1:5500/assets/page-result.html"

    with open("assets/page-stop.html", "r") as file:
        html = file.read()

    # response = mock_client.get(url)
    # html = response.text

    # Call the function to scrape stop statistics
    result = spa_scraper.scrape_stop_stats(html)
    pprint(result.items(), indent=2)


if __name__ == "__main__":
    test_get_spa_data()
