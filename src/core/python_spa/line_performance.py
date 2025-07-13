from typing import Optional

from bs4 import BeautifulSoup, Tag

from .spa_struct import LinePerformance


def extract_line_performance(html_text: str) -> LinePerformance:
    """
    Extracts line performance metrics from HTML

    Args:
        html_text: The HTML string containing line performance data

    Returns:
        LinePerformance object containing metrics like failure rate, run time, MTBF, and reject counts

    Raises:
        ValueError: If the Analysis row is not found or has insufficient columns
    """
    soup: BeautifulSoup = BeautifulSoup(html_text, "html.parser")
    line_performance: LinePerformance = LinePerformance()

    # Find the first <tr> containing "Analysis" in any <td>
    analysis_row: Optional[Tag] = next(
        (
            row
            for row in soup.find_all("tr")
            if any("Analysis" in td.get_text(strip=True) for td in row.find_all("td"))
        ),
        None,
    )

    if not analysis_row:
        raise ValueError("Could not find Analysis row in HTML")

    tds: list[Tag] = analysis_row.find_all("td")
    if len(tds) < 14:
        raise ValueError("Insufficient columns in Analysis row")

    line_performance.line_failure = tds[4].get_text(strip=True)
    line_performance.run_time = tds[6].get_text(strip=True)
    line_performance.line_mtbf = tds[8].get_text(strip=True)
    line_performance.reject = tds[10].get_text(strip=True)
    line_performance.total_reject = tds[13].get_text(strip=True)
    return line_performance
