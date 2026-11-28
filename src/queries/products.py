"""Requetes produits (Membre 3), en PyMongo.

Les filtres, les facettes et la hierarchie reprennent la logique validee par le module
Search & Categories (mongosh/search_products.js, facet_search.js, category_hierarchy.js).
Ajouts de ce module : produit par ID, recherche par mots-clés, pagination.
"""
import json
import re
from bson.decimal128 import Decimal128
from pymongo.errors import OperationFailure
from src.db import get_db

PROJECTION = {"_id": 0, "product_id": 1, "title": 1, "brand": 1, "category": 1, "price": 1, "rating": 1}
DEFAULT_SORT = [("rating.average", -1), ("product_id", 1)]


# ---------- validation et construction du filtre ----------
def _validate(c):
    for k in ("min_price", "max_price"):
        v = c.get(k)
        if v is not None and (isinstance(v, bool) or not isinstance(v, (int, float)) or v < 0):
            raise ValueError(f"Prix invalide : {k}")
    if c.get("min_price") is not None and c.get("max_price") is not None and c["min_price"] > c["max_price"]:
        raise ValueError("Le prix minimum depasse le prix maximum.")
    r = c.get("min_rating")
    if r is not None and (isinstance(r, bool) or not isinstance(r, (int, float)) or not 0 <= r <= 5):
        raise ValueError("La note doit etre comprise entre 0 et 5.")


def build_filter(criteria):
    """criteria : main, path (liste), brand, min_price, max_price, min_rating (tous optionnels)."""
    c = criteria or {}
    _validate(c)
    f = {}
    if c.get("main"):
        # categorie principale "effective" : category.main, ou path[0] si main est absent / vide
        f["$or"] = [
            {"category.main": c["main"]},
            {"category.main": None, "category.path.0": c["main"]},
            {"category.main": re.compile(r"^\s*$"), "category.path.0": c["main"]},
        ]
    for i, name in enumerate(c.get("path") or []):   # chemin exact => inclut les sous-categories
        f[f"category.path.{i}"] = name
    if c.get("brand"):
        f["brand"] = c["brand"]
    if c.get("min_price") is not None or c.get("max_price") is not None:
        f["price"] = {"$type": "number", "$gte": Decimal128(str(c.get("min_price") or 0))}
        if c.get("max_price") is not None:
            f["price"]["$lte"] = Decimal128(str(c["max_price"]))
    if c.get("min_rating") is not None:
        f["rating.average"] = {"$gte": c["min_rating"]}
    return f


def _page(col, flt, page, page_size, sort=None, projection=PROJECTION):
    page, page_size = max(int(page), 1), min(max(int(page_size), 1), 100)
    cur = col.find(flt, projection).sort(sort or DEFAULT_SORT).skip((page - 1) * page_size).limit(page_size)
    return {"total": col.count_documents(flt), "page": page, "page_size": page_size, "items": list(cur)}


# ---------- 1. produit par ID ----------
def find_product_by_id(product_id):
    return get_db().products.find_one({"product_id": product_id}, {"_id": 0})


# ---------- 2. recherche par mots-clés ----------
def search_by_keywords(text, page=1, page_size=10):
    """Index texte ($text) si disponible, sinon repli sur une recherche insensible a la casse."""
    text = (text or "").strip()
    if not text:
        raise ValueError("Mots-clés vides.")
    col = get_db().products
    try:
        flt = {"$text": {"$search": text}}
        proj = {**PROJECTION, "score": {"$meta": "textScore"}}
        return _page(col, flt, page, page_size, sort=[("score", {"$meta": "textScore"})], projection=proj)
    except OperationFailure:      # pas d'index texte sur products
        words = [re.escape(w) for w in text.split()]
        flt = {"$and": [{"title": re.compile(w, re.IGNORECASE)} for w in words]}
        return _page(col, flt, page, page_size)


# ---------- 3 et 4. filtres (catégorie, prix, marque, note) ----------
def filter_products(criteria, page=1, page_size=10, sort=None):
    return _page(get_db().products, build_filter(criteria), page, page_size, sort)


# ---------- 5. recherche à facettes ----------
def facets(criteria):
    pipeline = [
        {"$match": build_filter(criteria)},
        {"$facet": {
            "total": [{"$count": "count"}],
            "brands": [
                {"$match": {"brand": {"$exists": True, "$ne": None}}},
                {"$group": {"_id": "$brand", "count": {"$sum": 1}}},
                {"$sort": {"count": -1, "_id": 1}},
            ],
            "price_ranges": [
                {"$match": {"price": {"$type": "number", "$gte": Decimal128("0")}}},
                {"$bucket": {"groupBy": "$price",
                             "boundaries": [Decimal128(x) for x in ("0", "50", "100", "200", "500")],
                             "default": "500+", "output": {"count": {"$sum": 1}}}},
            ],
            "missing_prices": [{"$match": {"price": None}}, {"$count": "count"}],
            "ratings": [
                {"$match": {"rating.average": {"$type": "number"}}},
                {"$bucket": {"groupBy": "$rating.average", "boundaries": [0, 2, 3, 4, 5.01],
                             "default": "Other", "output": {"count": {"$sum": 1}}}},
            ],
        }},
        {"$set": {
            "total": {"$ifNull": [{"$arrayElemAt": ["$total.count", 0]}, 0]},
            "missing_prices": {"$ifNull": [{"$arrayElemAt": ["$missing_prices.count", 0]}, 0]},
        }},
    ]
    return next(get_db().products.aggregate(pipeline), None)


# ---------- 6. catégorie et sous-catégories ----------
def category_id(main, path):
    """Meme identifiant que sync_categories.js : JSON.stringify([main, ...path])."""
    return json.dumps([main, *path], separators=(",", ":"), ensure_ascii=False)


def category_with_descendants(main, path):
    """La catégorie et tous ses descendants (collection `categories`, champs ancestors / depth)."""
    cid = category_id(main, path)
    cur = get_db().categories.find(
        {"$or": [{"category_id": cid}, {"ancestors": cid}]},
        {"_id": 0, "category_id": 1, "name": 1, "path": 1, "depth": 1},
    ).sort([("depth", 1), ("name", 1)])
    return list(cur)


def products_in_category(main, path, page=1, page_size=10):
    """Produits de la catégorie ET de ses sous-catégories (le chemin est un préfixe)."""
    if not path:
        raise ValueError("path obligatoire")
    return _page(get_db().products, build_filter({"main": main, "path": path}), page, page_size,
                 sort=[("product_id", 1)])
