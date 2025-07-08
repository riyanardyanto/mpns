from bs4 import BeautifulSoup

from .line_performance import extract_line_performance
from .planned import extract_planned_downtime
from .product import extract_products
from .quality_loss import extract_quality_loss
from .rate_loss import extract_rate_loss
from .spa_struct import SPALossTree
from .time_range import extract_time_range
from .unplanned import extract_unplanned_downtime


def extract_equipment(html: str) -> str:
    """
    Extracts equipment name from HTML header

    Args:
        html: The HTML string to parse

    Returns:
        The equipment name as a string

    Raises:
        ValueError: If the equipment name cannot be found or the selector fails
    """
    soup = BeautifulSoup(html, "html.parser")
    b_tags = soup.select("b")

    if not b_tags:
        raise ValueError("Could not find equipment name in HTML")

    text = b_tags[0].get_text(strip=True)
    equipment = text.split("Period:")[0].strip() if "Period:" in text else ""

    if not equipment:
        raise ValueError("Could not find equipment name in HTML")

    return equipment


def extract_period(html: str) -> str:
    """
    Extracts period information from HTML header

    Args:
        html: The HTML string to parse

    Returns:
        The period information as a string

    Raises:
        ValueError: If the period information cannot be found or the selector fails
    """
    soup = BeautifulSoup(html, "html.parser")
    b_tags = soup.select("b")

    if not b_tags:
        raise ValueError("Could not find period information in HTML")

    text = b_tags[0].get_text(strip=True)
    period = (
        text.split("Period:")[1].strip()
        if "Period:" in text and len(text.split("Period:")) > 1
        else ""
    )

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
    try:
        equipment = extract_equipment(html)
    except ValueError:
        equipment = None

    try:
        period = extract_period(html)
    except ValueError:
        period = None

    try:
        time_range = extract_time_range(html)
    except ValueError:
        time_range = None

    try:
        product_by_po = extract_products(html)
    except ValueError:
        product_by_po = None

    try:
        line_performance = extract_line_performance(html)
    except ValueError:
        line_performance = None

    try:
        rate_loss = extract_rate_loss(html)
    except ValueError:
        rate_loss = None

    try:
        quality_loss = extract_quality_loss(html)
    except ValueError:
        quality_loss = None

    try:
        planned = extract_planned_downtime(html)
    except ValueError:
        planned = None

    try:
        unplanned = extract_unplanned_downtime(html)
    except ValueError:
        unplanned = None

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
