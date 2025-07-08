from typing import Optional

from bs4 import BeautifulSoup

from .spa_struct import LinePerformance


def extract_line_performance(html: str) -> LinePerformance:
    """
    Extracts line performance metrics from HTML

    Args:
        html: The HTML string containing line performance data

    Returns:
        LinePerformance object containing metrics like failure rate, run time, MTBF, and reject counts

    Raises:
        ValueError: If the Analysis row is not found or has insufficient columns
    """
    soup = BeautifulSoup(html, "html.parser")
    line_performance = LinePerformance()

    for row in soup.select("tr"):
        tds = row.select("td")
        if not tds:
            continue
        # Only extract text if "Analysis" is present
        if any("Analysis" in td.get_text(strip=True) for td in tds):
            if len(tds) < 14:
                raise ValueError("Insufficient columns in Analysis row")
            td_texts = [td.get_text(strip=True) for td in tds]
            line_performance.line_failure = td_texts[4]
            line_performance.run_time = td_texts[6]
            line_performance.line_mtbf = td_texts[8]
            line_performance.reject = td_texts[10]
            line_performance.total_reject = td_texts[13]
            return line_performance

    raise ValueError("Could not find Analysis row in HTML")
