from typing import List, Optional

from bs4 import BeautifulSoup
from bs4.element import Tag

from .spa_struct import Losses, Planned, PlannedStopReason


def extract_planned_downtime(html: str) -> Planned:
    """
    Extracts planned downtime information from HTML including overall metrics and detailed reasons

    Args:
        html: The HTML string containing planned downtime data

    Returns:
        Planned object containing both summary metrics and detailed stop reasons

    Raises:
        ValueError: If selectors cannot be parsed or data extraction fails
    """
    soup: BeautifulSoup = BeautifulSoup(html, "html.parser")
    trs: List[Tag] = soup.select("tr")

    pdt: Optional[Losses] = None
    planned_stops_reason: List[PlannedStopReason] = []
    last_description: str = ""
    in_reason_section: bool = False

    for i, row in enumerate(trs):
        tds: List[Tag] = row.select("td")
        td_texts: List[str] = [td.get_text(strip=True) for td in tds]

        # Find PDT summary
        if (
            not pdt
            and len(tds) >= 11
            and any("Planned downtime" in text for text in td_texts)
        ):
            pdt = Losses(
                stops=td_texts[4],
                downtime=td_texts[6],
                uptime_loss=td_texts[7],
                mttr=td_texts[10],
            )
            in_reason_section = True
            continue

        # Start extracting planned stop reasons after PDT summary
        if in_reason_section:
            if any("Unplanned" in text for text in td_texts):
                break
            if len(tds) >= 14:
                description: str = td_texts[4] if td_texts[4] else last_description
                last_description = description
                planned_stops_reason.append(
                    PlannedStopReason(
                        description=description,
                        time=td_texts[5],
                        stops=td_texts[6],
                        downtime=td_texts[8],
                        uptime_loss=td_texts[9],
                        mtbf=td_texts[11],
                        mttr=td_texts[12],
                        details=td_texts[13],
                    )
                )

    if not pdt or (in_reason_section and not planned_stops_reason):
        raise ValueError("Could not locate planned downtime summary or reasons section")

    return Planned(
        pdt=pdt,
        pdt_reason=planned_stops_reason if planned_stops_reason else None,
    )
