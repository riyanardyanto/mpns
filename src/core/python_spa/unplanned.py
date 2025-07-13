from typing import Any, Callable, List, Optional, Tuple

from bs4 import BeautifulSoup, Tag

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
    soup: BeautifulSoup = BeautifulSoup(html, "html.parser")
    trs: List[Tag] = soup.select("tr")
    updt: Losses = Losses()
    updt_shift: List[UPDT] = []
    updt_category: List[UPDT] = []
    bde: List[UPDT] = []
    pf: List[UPDT] = []
    updt_reason: List[UnplannedStopReason] = []

    # Helper to find start/end indices
    def find_range(
        keyword_start: Optional[str],
        keyword_end: Optional[str],
        min_len: int = 0,
        class_check: Optional[Callable[[List[Tag], List[str]], bool]] = None,
    ) -> Tuple[int, int]:
        start: Optional[int] = None
        end: Optional[int] = None
        for i, row in enumerate(trs):
            tds: List[Tag] = row.select("td")
            td_texts: List[str] = [td.get_text(strip=True) for td in tds]
            if start is None:
                if class_check:
                    if class_check(tds, td_texts):
                        start = i
                elif keyword_start and any(keyword_start in text for text in td_texts):
                    start = i + 1
            elif (
                end is None
                and keyword_end
                and any(keyword_end in text for text in td_texts)
            ):
                end = i
                break
        if start is None:
            start = 0
        if end is None:
            end = len(trs)
        return start, end

    # Extract updt
    for row in trs:
        tds: List[Tag] = row.select("td")
        if len(tds) >= 11:
            td_texts: List[str] = [td.get_text(strip=True) for td in tds]
            if "Unplanned downtime" in td_texts:
                updt.stops = td_texts[4]
                updt.downtime = td_texts[6]
                updt.uptime_loss = td_texts[7]
                updt.mtbf = td_texts[9]
                updt.mttr = td_texts[10]
                break

    # updt_shift
    def shift_class_check(tds: List[Tag], td_texts: List[str]) -> bool:
        return any("shift" in text.lower() for text in td_texts) and any(
            "doctext" in (td.get("class") or []) for td in tds
        )

    start, end = find_range(
        None, "Unplanned downtime per Category", class_check=shift_class_check
    )
    for i in range(start, end):
        tds: List[Tag] = trs[i].select("td")
        if len(tds) >= 11:
            td_texts: List[str] = [td.get_text(strip=True) for td in tds]
            updt_shift.append(
                UPDT(
                    category=td_texts[3],
                    losses=Losses(
                        stops=td_texts[4],
                        downtime=td_texts[6],
                        uptime_loss=td_texts[7],
                        mtbf=td_texts[9],
                        mttr=td_texts[10],
                    ),
                )
            )

    # updt_category
    start, end = find_range(
        "Unplanned downtime per Category", "Breakdown & Process Failures"
    )
    for i in range(start, end):
        tds: List[Tag] = trs[i].select("td")
        if len(tds) >= 11:
            td_texts: List[str] = [td.get_text(strip=True) for td in tds]
            updt_category.append(
                UPDT(
                    category=td_texts[3],
                    losses=Losses(
                        stops=td_texts[4],
                        downtime=td_texts[6],
                        uptime_loss=td_texts[7],
                        mtbf=td_texts[9],
                        mttr=td_texts[10],
                    ),
                )
            )

    # bde
    def bde_start_check(tds: List[Tag], td_texts: List[str]) -> bool:
        return len(tds) >= 4 and "Breakdown" in td_texts

    start, end = find_range(None, "Process failures", class_check=bde_start_check)
    for i in range(start, end):
        tds: List[Tag] = trs[i].select("td")
        if len(tds) >= 14:
            td_texts: List[str] = [td.get_text(strip=True) for td in tds]
            category: str = td_texts[3][:-5] if len(td_texts[3]) >= 5 else td_texts[3]
            bde.append(
                UPDT(
                    category=category,
                    losses=Losses(
                        time=td_texts[5],
                        stops=td_texts[6],
                        downtime=td_texts[8],
                        uptime_loss=td_texts[9],
                        mtbf=td_texts[11],
                        mttr=td_texts[12],
                        details=td_texts[13],
                    ),
                )
            )

    # pf
    def pf_start_check(tds: List[Tag], td_texts: List[str]) -> bool:
        return len(tds) >= 4 and any("Process failures" in text for text in td_texts)

    start, end = find_range(None, "Low volume events", class_check=pf_start_check)
    temp_categories: List[str] = []
    for i in range(start, end):
        tds: List[Tag] = trs[i].select("td")
        if len(tds) >= 14:
            td_texts: List[str] = [td.get_text(strip=True) for td in tds]
            category: str = td_texts[3][:-6] if len(td_texts[3]) >= 6 else td_texts[3]
            if not category and temp_categories:
                category = temp_categories[-1]
            temp_categories.append(category)
            pf.append(
                UPDT(
                    category=category,
                    losses=Losses(
                        time=td_texts[5],
                        stops=td_texts[6],
                        downtime=td_texts[8],
                        uptime_loss=td_texts[9],
                        mtbf=td_texts[11],
                        mttr=td_texts[12],
                        details=td_texts[13],
                    ),
                )
            )

    # updt_reason
    index: int = next(
        (
            i + 1
            for i, row in enumerate(trs)
            if any(
                "Unplanned machine stop reasons" in td.get_text(strip=True)
                for td in row.select("td")
            )
        ),
        0,
    )
    for i in range(index, len(trs)):
        row: Tag = trs[i]
        tds: List[Tag] = row.select("td")
        if not tds or len(tds) < 16:
            continue
        td_texts: List[str] = [td.get_text(strip=True) for td in tds]
        if "Unplanned downtime" in td_texts:
            break
        if "Unplanned machine stop reasons" in td_texts:
            continue
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
        updt_shift=updt_shift or None,
        updt_category=updt_category or None,
        bde=bde or None,
        pf=pf or None,
        updt_reason=updt_reason or None,
    )
