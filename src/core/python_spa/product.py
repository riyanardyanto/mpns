from typing import List, Optional, Tuple

from bs4 import BeautifulSoup
from bs4.element import Tag

from .spa_struct import ProductByPO, Products


def extract_products(html: str) -> ProductByPO:
    """
    Extracts product information from HTML and returns a ProductByPO object

    Args:
        html: The HTML string containing product data

    Returns:
        ProductByPO object containing a list of products with their PO, FA code, and time

    Raises:
        ValueError: If product data range cannot be found or is invalid
    """
    soup: BeautifulSoup = BeautifulSoup(html, "html.parser")
    trs: List[Tag] = soup.select("tr")

    start: Optional[int] = None
    end: Optional[int] = None
    for i, row in enumerate(trs):
        tds: List[Tag] = row.select("td")
        row_text: str = "".join(td.get_text(strip=True) for td in tds)
        if start is None and "Theo Production by PO" in row_text:
            start = i + 1
        if end is None and "Line performance" in row_text:
            end = i
        if start is not None and end is not None:
            break

    if start is None:
        raise ValueError("Could not find row containing 'Theo Production by PO'")
    if end is None:
        raise ValueError("Could not find row containing 'Line performance'")
    if start >= end or end > len(trs):
        raise ValueError("Invalid row range for product data")

    products: List[Products] = [
        Products(
            po=(tds[3].split("-", 1)[0].strip() if tds[3].split("-", 1) else ""),
            fa_code=(
                tds[3].split("-", 1)[1].strip() if len(tds[3].split("-", 1)) > 1 else ""
            ),
            time=tds[4].get_text(strip=True),
        )
        for row in trs[start:end]
        if (tds := row.select("td")) and len(tds) >= 5
    ]

    return ProductByPO(products=products if products else None)
