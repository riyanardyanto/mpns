from typing import List, Optional, Tuple

from bs4 import BeautifulSoup

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
    soup = BeautifulSoup(html, "html.parser")
    trs = soup.select("tr")

    # Extract PDT summary in a single pass
    pdt = None
    for row in trs:
        tds = row.select("td")
        if len(tds) >= 11 and any(
            "Planned downtime" in td.get_text(strip=True) for td in tds
        ):
            td_texts = [td.get_text(strip=True) for td in tds]
            pdt = Losses(
                stops=td_texts[4],
                downtime=td_texts[6],
                uptime_loss=td_texts[7],
                mttr=td_texts[10],
            )
            break

    # Find planned stop reasons range
    start = end = None
    for i, row in enumerate(trs):
        td_texts = [td.get_text(strip=True) for td in row.select("td")]
        if start is None and any(text == "Planned downtime" for text in td_texts):
            start = i + 1
        if start is not None and any(text == "Unplanned" for text in td_texts):
            end = i
            break
    if start is None or end is None or start >= end:
        raise ValueError("Could not locate planned stop reasons section")

    # Extract planned stop reasons
    planned_stops_reason = []
    last_description = ""
    for i in range(start, end):
        row = trs[i]
        tds = row.select("td")
        if len(tds) < 14:
            continue
        td_texts = [td.get_text(strip=True) for td in tds]
        description = td_texts[4] if td_texts[4] else last_description
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

    return Planned(
        pdt=pdt,
        pdt_reason=planned_stops_reason if planned_stops_reason else None,
    )
