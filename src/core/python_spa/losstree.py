from bs4 import BeautifulSoup

from .line_performance import extract_line_performance
from .planned import extract_planned_downtime
from .product import extract_products
from .quality_loss import extract_quality_loss
from .rate_loss import extract_rate_loss
from .spa_struct import SPALossTree
from .time_range import extract_time_range
from .unplanned import extract_unplanned_downtime


def extract_equipment(soup) -> str:
    b_tags = soup.select("b")
    if not b_tags:
        raise ValueError("Could not find equipment name in HTML")
    text = b_tags[0].get_text(strip=True)
    equipment = text.split("Period:")[0].strip() if "Period:" in text else ""
    if not equipment:
        raise ValueError("Could not find equipment name in HTML")
    return equipment


def extract_period(soup) -> str:
    b_tags = soup.select("b")
    if not b_tags:
        raise ValueError("Could not find period information in HTML")
    text = b_tags[0].get_text(strip=True)
    parts = text.split("Period:")
    period = parts[1].strip() if len(parts) > 1 else ""
    if not period:
        raise ValueError("Could not find period information in HTML")
    return period


def extract_loss_tree(html: str) -> SPALossTree:
    """
    Extracts complete SPA Loss Tree from HTML

    Args:
        html: The HTML string containing all SPA data

    Returns:
        SPALossTree object containing all extracted metrics
    """
    soup = BeautifulSoup(html, "html.parser")

    def safe_extract(func, *args):
        try:
            return func(*args)
        except Exception:
            return None

    equipment = safe_extract(extract_equipment, soup)
    period = safe_extract(extract_period, soup)
    time_range = safe_extract(extract_time_range, html)
    product_by_po = safe_extract(extract_products, html)
    line_performance = safe_extract(extract_line_performance, html)
    rate_loss = safe_extract(extract_rate_loss, html)
    quality_loss = safe_extract(extract_quality_loss, html)
    planned = safe_extract(extract_planned_downtime, html)
    unplanned = safe_extract(extract_unplanned_downtime, html)

    return SPALossTree(
        equipment=equipment,
        period=period,
        time_range=time_range,
        product_by_po=product_by_po,
        line_performance=line_performance,
        rate_loss=rate_loss,
        quality_loss=quality_loss,
        planned=planned,
        unplanned=unplanned,
    )
