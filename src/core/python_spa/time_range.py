from typing import Callable, Dict, List, Optional, Tuple

from bs4 import BeautifulSoup

from .spa_struct import TimeRange


def extract_time_range(html: str) -> TimeRange:
    """
    Extracts time range data from HTML and returns a TimeRange object
    """
    soup: BeautifulSoup = BeautifulSoup(html, "html.parser")
    time_range: TimeRange = TimeRange()

    trs: List = soup.select("tr")
    if not trs:
        raise ValueError("No table rows found in HTML")

    # Map keywords to their handlers and minimum length
    # HandlerType = Callable[[List[str]], None]
    handlers: Dict[str, Tuple[int, Callable[[List[str]], None]]] = {
        "Calendar time": (
            12,
            lambda tds: setattr(time_range, "calendar_time", tds[11]),
        ),
        "Valid time": (5, lambda tds: setattr(time_range, "valid_time", tds[4])),
        "Missing data time": (
            5,
            lambda tds: setattr(time_range, "missing_data_time", tds[4]),
        ),
        "Excluded time": (5, lambda tds: setattr(time_range, "excluded_time", tds[4])),
        "Reference run time": (
            12,
            lambda tds: (
                setattr(time_range, "reference_run_time", tds[4]),
                setattr(time_range, "uptime", tds[7]),
                setattr(
                    time_range,
                    "theo_production_design_speed",
                    tds[11].split(":")[-1].split(" ")[0].strip() if tds[11] else "",
                ),
            ),
        ),
        "Theo production run time": (
            12,
            lambda tds: (
                setattr(time_range, "theo_production_run_time", tds[4]),
                setattr(
                    time_range,
                    "availability",
                    tds[11].split(";")[0].split("=")[1].strip()
                    if len(tds[11].split(";")) > 0 and "=" in tds[11].split(";")[0]
                    else "",
                ),
                setattr(
                    time_range,
                    "efficiency",
                    tds[11].split(";")[1].split("=")[1].strip()
                    if len(tds[11].split(";")) > 1 and "=" in tds[11].split(";")[1]
                    else "",
                ),
            ),
        ),
        "Working time": (
            12,
            lambda tds: (
                setattr(time_range, "pr", tds[7]),
                setattr(time_range, "mtbf", tds[9]),
                setattr(time_range, "mttr", tds[10]),
                setattr(
                    time_range,
                    "theo_production_target_speed",
                    tds[11].split(" ")[8].lstrip(":").strip()
                    if len(tds[11].split(" ")) > 8
                    else "",
                ),
                setattr(
                    time_range,
                    "net_production",
                    tds[11].split(" ")[1].split(":")[1].lstrip(":").strip()
                    if len(tds[11].split(" ")) > 1 and ":" in tds[11].split(" ")[1]
                    else "",
                ),
            ),
        ),
    }

    for row in trs:
        tds: List[str] = [td.get_text(strip=True) for td in row.select("td")]
        if not tds:
            continue
        for keyword, (min_len, handler) in handlers.items():
            if len(tds) >= min_len and any(keyword in text for text in tds):
                handler(tds)
                break

    return time_range
