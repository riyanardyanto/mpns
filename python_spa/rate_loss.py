from typing import List, Optional

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
    soup = BeautifulSoup(html, "html.parser")
    losses = RateLoss()

    keyword_map = {
        "Design speed loss": "dsl",
        "Target rate loss": "trl",
        "Not at Target Rate": "natr",
        "Start-up/Ramp-down": "ramp_up_down",
    }

    found = set()

    for row in soup.select("tr"):
        tds = row.select("td")
        if len(tds) < 7:
            continue
        td_texts = [td.get_text(strip=True) for td in tds]
        for keyword, attr in keyword_map.items():
            if keyword in " ".join(td_texts) and attr not in found:
                setattr(
                    losses,
                    attr,
                    Losses(
                        time="",
                        stops="",
                        downtime=td_texts[5],
                        uptime_loss=td_texts[6],
                        mtbf="",
                        mttr="",
                        details="",
                    ),
                )
                found.add(attr)
                if len(found) == len(keyword_map):
                    return losses

    return losses
