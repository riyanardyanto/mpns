from typing import List, Optional

from bs4 import BeautifulSoup

from .spa_struct import UPDT, Losses, Unplanned, UnplannedStopReason


def extract_unplanned_downtime(html: str) -> Unplanned:
    """
    Extracts unplanned downtime information from HTML including:
    - Overall UPDT metrics
    - Shift-based breakdowns
    - Category breakdowns
    - BDE (Breakdown Events)
    - PF (Process Failures)
    - Detailed stop reasons

    Args:
        html: The HTML string containing unplanned downtime data

    Returns:
        Unplanned object containing all extracted unplanned downtime metrics

    Raises:
        ValueError: If selectors cannot be parsed
    """
    soup = BeautifulSoup(html, "html.parser")
    trs = soup.select("tr")
    updt = Losses()
    updt_shift, updt_category, bde, pf, updt_reason = [], [], [], [], []

    # Helper to find start/end indices
    def find_range(keyword_start, keyword_end, min_len=0, class_check=None):
        start = end = None
        for i, row in enumerate(trs):
            tds = row.select("td")
            td_texts = [td.get_text(strip=True) for td in tds]
            if start is None:
                if class_check:
                    if class_check(tds, td_texts):
                        start = i
                elif any(keyword_start in text for text in td_texts):
                    start = i + 1
            elif end is None and any(keyword_end in text for text in td_texts):
                end = i
                break
        if start is None:
            start = 0
        if end is None:
            end = len(trs)
        return start, end

    # Extract updt
    for row in trs:
        tds = row.select("td")
        td_texts = [td.get_text(strip=True) for td in tds]
        if len(tds) >= 11 and any(text == "Unplanned downtime" for text in td_texts):
            updt.stops = td_texts[4]
            updt.downtime = td_texts[6]
            updt.uptime_loss = td_texts[7]
            updt.mtbf = td_texts[9]
            updt.mttr = td_texts[10]
            break

    # updt_shift
    def shift_class_check(tds, td_texts):
        return any("shift" in text.lower() for text in td_texts) and any(
            "doctext" in (td.get("class") or []) for td in tds
        )

    start, end = find_range(
        None, "Unplanned downtime per Category", class_check=shift_class_check
    )
    for i in range(start, end):
        tds = trs[i].select("td")
        td_texts = [td.get_text(strip=True) for td in tds]
        if len(tds) >= 11:
            category = td_texts[3]
            losses = Losses(
                stops=td_texts[4],
                downtime=td_texts[6],
                uptime_loss=td_texts[7],
                mtbf=td_texts[9],
                mttr=td_texts[10],
            )
            updt_shift.append(UPDT(category=category, losses=losses))

    # updt_category
    start, end = find_range(
        "Unplanned downtime per Category", "Breakdown & Process Failures"
    )
    for i in range(start, end):
        tds = trs[i].select("td")
        td_texts = [td.get_text(strip=True) for td in tds]
        if len(tds) >= 11:
            category = td_texts[3]
            losses = Losses(
                stops=td_texts[4],
                downtime=td_texts[6],
                uptime_loss=td_texts[7],
                mtbf=td_texts[9],
                mttr=td_texts[10],
            )
            updt_category.append(UPDT(category=category, losses=losses))

    # bde
    def bde_start_check(tds, td_texts):
        return len(tds) >= 4 and any(text == "Breakdown" for text in td_texts)

    start, end = find_range(None, "Process failures", class_check=bde_start_check)
    for i in range(start, end):
        tds = trs[i].select("td")
        td_texts = [td.get_text(strip=True) for td in tds]
        if len(tds) >= 14:
            category = td_texts[3][:-5] if len(td_texts[3]) >= 5 else td_texts[3]
            losses = Losses(
                time=td_texts[5],
                stops=td_texts[6],
                downtime=td_texts[8],
                uptime_loss=td_texts[9],
                mtbf=td_texts[11],
                mttr=td_texts[12],
                details=td_texts[13],
            )
            bde.append(UPDT(category=category, losses=losses))

    # pf
    def pf_start_check(tds, td_texts):
        return len(tds) >= 4 and any("Process failures" in text for text in td_texts)

    start, end = find_range(None, "Low volume events", class_check=pf_start_check)
    temp_categories = []
    for i in range(start, end):
        tds = trs[i].select("td")
        td_texts = [td.get_text(strip=True) for td in tds]
        if len(tds) >= 14:
            category = td_texts[3][:-6] if len(td_texts[3]) >= 6 else td_texts[3]
            if not category and temp_categories:
                category = temp_categories[-1]
            temp_categories.append(category)
            losses = Losses(
                time=td_texts[5],
                stops=td_texts[6],
                downtime=td_texts[8],
                uptime_loss=td_texts[9],
                mtbf=td_texts[11],
                mttr=td_texts[12],
                details=td_texts[13],
            )
            pf.append(UPDT(category=category, losses=losses))

    # updt_reason
    index = 0
    for i, row in enumerate(trs):
        td_texts = [td.get_text(strip=True) for td in row.select("td")]
        if any("Unplanned machine stop reasons" in text for text in td_texts):
            index = i + 1
            break
    for i in range(index, len(trs)):
        row = trs[i]
        td_texts = [td.get_text(strip=True) for td in row.select("td")]
        if any("Unplanned downtime" in text for text in td_texts):
            break
        if any("Unplanned machine stop reasons" in text for text in td_texts):
            continue
        tds = row.select("td")
        if len(tds) >= 16:
            updt_reason.append(
                UnplannedStopReason(
                    description=td_texts[3],
                    stops=td_texts[4],
                    ramp_up=td_texts[5],
                    downtime=td_texts[6],
                    uptime_loss=td_texts[7],
                    mtbf=td_texts[9],
                    mttr=td_texts[10],
                    rejects_percent=td_texts[11],
                    stops_per_shift=td_texts[12],
                    causing_equipment=td_texts[15],
                )
            )

    return Unplanned(
        updt=updt,
        updt_shift=updt_shift if updt_shift else None,
        updt_category=updt_category if updt_category else None,
        bde=bde if bde else None,
        pf=pf if pf else None,
        updt_reason=updt_reason if updt_reason else None,
    )
