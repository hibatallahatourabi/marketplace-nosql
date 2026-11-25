"""Mise a jour du stock (Membre 3). Disponible = quantity - reserved."""
from datetime import datetime, timezone
from src.db import get_db


def _now():
    return datetime.now(timezone.utc)


def get_available(product_id):
    d = get_db().inventory.find_one({"product_id": product_id})
    return None if d is None else d["quantity"] - d["reserved"]


def increase_stock(product_id, qty):
    if qty <= 0: raise ValueError("qty > 0")
    return get_db().inventory.update_one(
        {"product_id": product_id},
        {"$inc": {"quantity": qty}, "$set": {"last_update": _now()}}, upsert=True)


def reserve_stock(product_id, qty):
    """Atomique : reserve seulement si assez de stock disponible."""
    if qty <= 0: raise ValueError("qty > 0")
    r = get_db().inventory.update_one(
        {"product_id": product_id, "$expr": {"$gte": [{"$subtract": ["$quantity", "$reserved"]}, qty]}},
        {"$inc": {"reserved": qty}, "$set": {"last_update": _now()}})
    return r.modified_count == 1


def confirm_sale(product_id, qty):
    r = get_db().inventory.update_one(
        {"product_id": product_id, "reserved": {"$gte": qty}, "quantity": {"$gte": qty}},
        {"$inc": {"quantity": -qty, "reserved": -qty}, "$set": {"last_update": _now()}})
    return r.modified_count == 1
