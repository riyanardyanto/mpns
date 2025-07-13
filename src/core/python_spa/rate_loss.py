from typing import Dict, List, Optional, Set

from bs4 import BeautifulSoup

from .spa_struct import Losses, RateLoss


def extract_rate_loss(html: str) -> RateLoss:
    """
    Extracts rate loss metrics from HTML including design speed loss, target rate loss,
    not at target rate, and ramp up/down losses.

    Args:
        html: The HTML string containing rate loss data

    Returns:
        RateLoss object containing all extracted rate loss metrics

    Raises:
        ValueError: If selectors cannot be parsed
    """
    soup: BeautifulSoup = BeautifulSoup(html, "html.parser")
    losses: RateLoss = RateLoss()

    keyword_map: Dict[str, str] = {
        "Design speed loss": "dsl",
        "Target rate loss": "trl",
        "Not at Target Rate": "natr",
        "Start-up/Ramp-down": "ramp_up_down",
    }

    found: Set[str] = set()
    keywords: Set[str] = set(keyword_map.keys())

    for row in soup.select("tr"):
        tds = row.select("td")
        if len(tds) < 7:
            continue
        row_text: str = " ".join(td.get_text(strip=True) for td in tds)
        for keyword in keywords - found:
            if keyword in row_text:
                attr: str = keyword_map[keyword]
                setattr(
                    losses,
                    attr,
                    Losses(
                        time="",
                        stops="",
                        downtime=tds[5].get_text(strip=True),
                        uptime_loss=tds[6].get_text(strip=True),
                        mtbf="",
                        mttr="",
                        details="",
                    ),
                )
                found.add(keyword)
                if len(found) == len(keyword_map):
                    return losses

    return losses
