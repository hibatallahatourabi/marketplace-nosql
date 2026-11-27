"""Index des collections `reviews` et `inventory` (idempotent : peut etre relance)."""
from pymongo import ASCENDING, DESCENDING

# Un index par option de tri de get_reviews_page. Le tri secondaire sur _id rend la pagination stable.
# rating_asc (rating 1, _id -1) est l'inverse exact de rating_desc : meme index, parcours inverse.
REVIEW_INDEXES = {
    "reviews_product_recent": [("product_id", ASCENDING), ("created_at", DESCENDING), ("_id", ASCENDING)],
    "reviews_product_helpful": [("product_id", ASCENDING), ("helpful_vote", DESCENDING), ("_id", ASCENDING)],
    "reviews_product_rating": [("product_id", ASCENDING), ("rating", DESCENDING), ("_id", ASCENDING)],
}
# Anciens index crees par la premiere version du script d'import (preferes aux nouveaux : redondants)
OLD_REVIEW_INDEXES = ["product_id_1_created_at_-1", "product_id_1_rating_-1"]


def ensure_review_indexes(db):
    existing = {i["name"] for i in db.reviews.list_indexes()}
    for name in OLD_REVIEW_INDEXES:
        if name in existing:
            db.reviews.drop_index(name)
    for name, keys in REVIEW_INDEXES.items():
        db.reviews.create_index(keys, name=name)
    return sorted(i["name"] for i in db.reviews.list_indexes())


def ensure_inventory_unique_index(db):
    """Garantit un index UNIQUE sur inventory.product_id, sans toucher aux index des autres membres.

    - index unique deja present (quel que soit son nom) -> on le garde ;
    - index non unique sur product_id -> on s'arrete (a transformer avec son auteur) ;
    - doublons dans les donnees -> on s'arrete et on les liste ;
    - sinon -> creation.
    """
    for idx in db.inventory.list_indexes():
        if list(idx["key"].items()) == [("product_id", 1)] and idx["name"] != "_id_":
            if idx.get("unique"):
                return idx["name"]
            raise RuntimeError(
                f"L'index '{idx['name']}' sur product_id existe mais n'est PAS unique. "
                "Le remplacer par un index unique se decide avec son auteur (Membre 4).")
    dups = list(db.inventory.aggregate([
        {"$group": {"_id": "$product_id", "n": {"$sum": 1}}},
        {"$match": {"n": {"$gt": 1}}},
    ]))
    if dups:
        raise RuntimeError(f"Doublons dans inventory, a corriger d'abord : {[d['_id'] for d in dups][:10]}")
    return db.inventory.create_index([("product_id", ASCENDING)], unique=True, name="inventory_product_id_unique")


def ensure_products_text_index(db):
    """Index texte (title, brand) pour la recherche par mots-clés.
    MongoDB n'autorise qu'UN index texte par collection : on reutilise celui qui existe deja.
    A coordonner avec le module Search & Categories avant de le creer sur Atlas."""
    for idx in db.products.list_indexes():
        if "weights" in idx or any(v == "text" for v in idx["key"].values()):
            return idx["name"]
    return db.products.create_index([("title", "text"), ("brand", "text")], name="idx_products_text",
                                    weights={"title": 10, "brand": 3})


def explain_summary(explain):
    """Resume le plan RETENU d'un explain() : (etapes, noms d'index). Ignore rejectedPlans."""
    winning = explain.get("queryPlanner", {}).get("winningPlan", {})
    stages, indexes = [], []

    def walk(node):
        if isinstance(node, dict):
            if "stage" in node:
                stages.append(node["stage"])
            if "indexName" in node:
                indexes.append(node["indexName"])
            for k, v in node.items():
                if k != "slotBasedPlan":
                    walk(v)
        elif isinstance(node, list):
            for v in node:
                walk(v)

    walk(winning)
    return stages, indexes
