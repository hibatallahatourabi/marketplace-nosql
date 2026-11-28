"""Requetes Membre 3 : reviews paginees, stats de notes, produit + reviews."""
from src.db import get_db, PRODUCT_KEY

SORTS = {"recent": ("created_at", -1), "helpful": ("helpful_vote", -1),
         "rating_desc": ("rating", -1), "rating_asc": ("rating", 1)}


def sort_spec(sort):
    """Tri principal + tri secondaire sur _id (pagination stable).
    Le tri secondaire est de sens oppose, ce qui correspond exactement a un index
    (champ dir, _id asc) parcouru dans un sens ou dans l'autre (voir src/operations/indexes.py)."""
    field, direction = SORTS[sort]
    return [(field, direction), ("_id", 1 if direction == -1 else -1)]


def get_reviews_page(product_id, page=1, page_size=10, sort="recent"):
    page, page_size = max(page, 1), min(max(page_size, 1), 100)
    col = get_db().reviews
    total = col.count_documents({"product_id": product_id})
    items = list(col.find({"product_id": product_id})
                 .sort(sort_spec(sort))
                 .skip((page - 1) * page_size).limit(page_size))
    return {"total": total, "page": page, "page_size": page_size, "items": items}


def get_rating_stats(product_id):
    pipeline = [
        {"$match": {"product_id": product_id}},
        {"$group": {"_id": "$rating", "n": {"$sum": 1}}},
    ]
    dist = {int(d["_id"]): d["n"] for d in get_db().reviews.aggregate(pipeline)}
    count = sum(dist.values())
    avg = sum(k * v for k, v in dist.items()) / count if count else None
    return {"product_id": product_id, "review_count": count,
            "average_rating": round(avg, 2) if avg is not None else None,
            "distribution": {s: dist.get(s, 0) for s in (5, 4, 3, 2, 1)}}


def get_product_with_reviews(product_id, limit=5):
    """Association produit <-> reviews via $lookup."""
    pipeline = [
        {"$match": {PRODUCT_KEY: product_id}},
        {"$lookup": {"from": "reviews", "localField": PRODUCT_KEY, "foreignField": "product_id",
                     "pipeline": [{"$sort": {"created_at": -1}}, {"$limit": limit}],
                     "as": "reviews"}},
    ]
    return next(get_db().products.aggregate(pipeline), None)
