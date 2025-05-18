import json
from pprint import pprint

import httpx
import spa_scraper_pyo3


def test_get_spa_data():
    # Mock the HTTPX client
    # mock_client = httpx.Client()

    # url = "http://127.0.0.1:5500/assets/page-result.html"

    with open("assets/page-stop.html", "r") as file:
        html = file.read()

    # response = mock_client.get(url)
    # html = response.text

    # Call the function to scrape stop statistics
    result = spa_scraper_pyo3.extract_stop_stats(html)
    # pprint(result.to_python_dict())

    with open("_stop_stats.json", "w") as f:
        f.write(json.dumps(result.to_python_dict()))


if __name__ == "__main__":
    test_get_spa_data()
