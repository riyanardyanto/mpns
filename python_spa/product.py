from typing import List, Optional, Tuple

from bs4 import BeautifulSoup

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
    soup = BeautifulSoup(html, "html.parser")
    trs = soup.select("tr")

    # Find start and end indices in a single pass
    start = end = None
    for i, row in enumerate(trs):
        row_text = "".join(td.get_text(strip=True) for td in row.select("td"))
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

    products = []
    for row in trs[start:end]:
        tds = row.select("td")
        if len(tds) >= 5:
            td_texts = [td.get_text(strip=True) for td in tds]
            parts = td_texts[3].split("-", 1)
            products.append(
                Products(
                    po=parts[0].strip() if parts else "",
                    fa_code=parts[1].strip() if len(parts) > 1 else "",
                    time=td_texts[4],
                )
            )

    return ProductByPO(products=products if products else None)
