from typing import Optional

from bs4 import BeautifulSoup

from .spa_struct import TimeRange


def extract_time_range(html: str) -> TimeRange:
    """
    Extracts time range data from HTML and returns a TimeRange object

    Args:
        html: The HTML string to parse

    Returns:
        TimeRange object containing all extracted time metrics

    Raises:
        ValueError: If selectors cannot be parsed or data extraction fails
    """
    soup = BeautifulSoup(html, "html.parser")
    time_range = TimeRange()

    trs = soup.select("tr")
    if not trs:
        raise ValueError("No table rows found in HTML")

    # Map keywords to their handlers for efficiency
    def handle_calendar_time(tds):
        time_range.calendar_time = tds[11]

    def handle_valid_time(tds):
        time_range.valid_time = tds[4]

    def handle_missing_data_time(tds):
        time_range.missing_data_time = tds[4]

    def handle_excluded_time(tds):
        time_range.excluded_time = tds[4]

    def handle_reference_run_time(tds):
        time_range.reference_run_time = tds[4]
        time_range.uptime = tds[7]
        text = tds[11]
        parts = text.split(":")
        time_range.theo_production_design_speed = (
            parts[-1].split(" ")[0] if parts else ""
        )

    def handle_theo_production_run_time(tds):
        time_range.theo_production_run_time = tds[4]
        text = tds[11]
        parts = text.split(";")
        time_range.availability = (
            parts[0].split("=")[1].strip() if len(parts) > 0 and "=" in parts[0] else ""
        )
        time_range.efficiency = (
            parts[1].split("=")[1].strip() if len(parts) > 1 and "=" in parts[1] else ""
        )

    def handle_working_time(tds):
        time_range.pr = tds[7]
        time_range.mtbf = tds[9]
        time_range.mttr = tds[10]
        text = tds[11]
        words = text.split(" ")
        time_range.theo_production_target_speed = (
            words[8].lstrip(":") if len(words) > 8 else ""
        )
        time_range.net_production = (
            words[1].split(":")[1].lstrip(":")
            if len(words) > 1 and ":" in words[1]
            else ""
        )

    handlers = [
        ("Calendar time", 12, handle_calendar_time),
        ("Valid time", 5, handle_valid_time),
        ("Missing data time", 5, handle_missing_data_time),
        ("Excluded time", 5, handle_excluded_time),
        ("Reference run time", 12, handle_reference_run_time),
        ("Theo production run time", 12, handle_theo_production_run_time),
        ("Working time", 12, handle_working_time),
    ]

    for row in trs:
        tds = row.select("td")
        if not tds:
            continue
        td_texts = [td.get_text(strip=True) for td in tds]
        for keyword, min_len, handler in handlers:
            if len(tds) >= min_len and any(keyword in text for text in td_texts):
                handler(td_texts)
                break  # Only handle the first matching keyword per row

    return time_range
