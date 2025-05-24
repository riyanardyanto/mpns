import json
from pprint import pprint

import httpx
import spa_scraper_pyo3


def test_get_spa_data():
    # Mock the HTTPX client
    mock_client = httpx.Client()

    url = "http://127.0.0.1:5500/assets/loss_tree_shift_6.html"

    # with open("assets/page-stop.html", "r") as file:
    #     html = file.read()

    response = mock_client.get(url)
    html = response.text

    # Call the function to scrape stop statistics
    result = spa_scraper_pyo3.extract_loss_tree(html)
    # pprint(result.planned.pdt_reason[0].to_python_dict())

    for reason in result.planned.pdt_reason:
        pprint(reason.to_python_dict())

    with open("_stop_stats.json", "w") as f:
        f.write(json.dumps(result.to_python_dict()))


if __name__ == "__main__":
    test_get_spa_data()
