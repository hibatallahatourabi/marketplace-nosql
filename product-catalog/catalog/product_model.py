
from bson.decimal128 import Decimal128


def create_product_document(
    product_id,
    title,
    brand,
    category,
    price=None,
    rating=None,
    features=None,
    description=None,
    attributes=None,
    images=None,
    source="Amazon Reviews 2023"
):
    """
    Creates a standardized product document.
    """

    if not product_id or not title:
        raise ValueError("Product ID and title are required.")

    if price is not None and not isinstance(price, Decimal128):
        raise TypeError("Price must be Decimal128 or None.")

    return {
        "product_id": product_id,
        "title": title,
        "brand": brand,
        "category": category,
        "price": price,
        "rating": rating or {},
        "features": features or [],
        "description": description or [],
        "attributes": attributes or {},
        "images": images or {},
        "source": source
    }
