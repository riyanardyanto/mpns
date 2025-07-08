from typing import Optional

from bs4 import BeautifulSoup

from .spa_struct import Losses, QualityLoss


def extract_quality_loss(html: str) -> QualityLoss:
    """
    Extracts quality loss metrics from HTML

    Args:
        html: The HTML string containing quality loss data

    Returns:
        QualityLoss object containing reject loss metrics including downtime and uptime loss
    """
    soup = BeautifulSoup(html, "html.parser")
    reject_loss = None

    for row in soup.select("tr"):
        tds = row.select("td")
        if len(tds) >= 7 and any(
            td.get_text(strip=True) == "Reject losses" for td in tds
        ):
            td_texts = [td.get_text(strip=True) for td in tds]
            reject_loss = Losses(downtime=td_texts[5], uptime_loss=td_texts[6])
            break

    return QualityLoss(reject_loss=reject_loss)
