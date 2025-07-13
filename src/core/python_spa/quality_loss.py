from typing import List, Optional

from bs4 import BeautifulSoup, Tag

from .spa_struct import Losses, QualityLoss


def extract_quality_loss(html: str) -> Optional[QualityLoss]:
    """
    Extracts quality loss metrics from HTML

    Args:
        html: The HTML string containing quality loss data

    Returns:
        QualityLoss object containing reject loss metrics including downtime and uptime loss
    """
    soup: BeautifulSoup = BeautifulSoup(html, "lxml")
    reject_loss: Optional[Losses] = None

    for row in soup.select("tr"):
        tds: List[Tag] = row.select("td")
        if len(tds) >= 7:
            for td in tds:
                cell_text: str = td.get_text(strip=True)
                if cell_text == "Reject losses":
                    reject_loss = Losses(
                        downtime=tds[5].get_text(strip=True),
                        uptime_loss=tds[6].get_text(strip=True),
                    )
                    return QualityLoss(reject_loss=reject_loss)

    return None
