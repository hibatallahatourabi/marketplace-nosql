"""Mise a jour du stock (Membre 3). Disponible = quantity - reserved.

Champs de `inventory` : product_id, quantity, reserved, last_updated
(meme nommage que inventory/stock/stock_operations.js du Membre 4).
"""
from datetime import datetime, timezone
from src.db import get_db


def _now():
    return datetime.now(timezone.utc)


def _check_qty(qty):
    """La quantite doit etre un entier strictement positif (bool refuse)."""
    if isinstance(qty, bool) or not isinstance(qty, int) or qty <= 0:
        raise ValueError("qty doit etre un entier > 0")


def get_available(product_id):
    d = get_db().inventory.find_one({"product_id": product_id})
    return None if d is None else d["quantity"] - d["reserved"]


def increase_stock(product_id, qty):
    """Ajoute du stock. Cree la fiche si elle n'existe pas, avec reserved = 0."""
    _check_qty(qty)
    return get_db().inventory.update_one(
        {"product_id": product_id},
        {"$inc": {"quantity": qty},
         "$setOnInsert": {"reserved": 0},
         "$set": {"last_updated": _now()}},
        upsert=True)


def reserve_stock(product_id, qty):
    """Atomique : reserve seulement si assez de stock disponible."""
    _check_qty(qty)
    r = get_db().inventory.update_one(
        {"product_id": product_id, "$expr": {"$gte": [{"$subtract": ["$quantity", "$reserved"]}, qty]}},
        {"$inc": {"reserved": qty}, "$set": {"last_updated": _now()}})
    return r.modified_count == 1


def confirm_sale(product_id, qty):
    """Transforme une reservation en vente : quantity -= qty et reserved -= qty."""
    _check_qty(qty)
    r = get_db().inventory.update_one(
        {"product_id": product_id, "reserved": {"$gte": qty}, "quantity": {"$gte": qty}},
        {"$inc": {"quantity": -qty, "reserved": -qty}, "$set": {"last_updated": _now()}})
    return r.modified_count == 1
