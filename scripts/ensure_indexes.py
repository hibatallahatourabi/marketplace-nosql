"""Cree les index de `reviews` et `inventory` (sans reimporter) et verifie qu'ils servent les tris.

  python scripts/ensure_indexes.py            # cree / met a jour les index
  python scripts/ensure_indexes.py --explain  # + verifie chaque tri avec explain()
"""
import argparse, json, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.db import get_db
from src.operations.indexes import ensure_review_indexes, ensure_inventory_unique_index, ensure_products_text_index
from src.queries.reviews import sort_spec, SORTS


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--explain", action="store_true")
    ap.add_argument("--text-index", action="store_true",
                    help="cree l'index texte de products (a coordonner avec Search & Categories)")
    a = ap.parse_args()
    db = get_db()

    print("reviews :", ensure_review_indexes(db))
    try:
        print("inventory :", ensure_inventory_unique_index(db))
    except RuntimeError as e:
        print("inventory : IGNORE ->", e)

    if a.text_index:
        print("products (texte) :", ensure_products_text_index(db))

    if a.explain:
        sample = db.reviews.find_one({}, {"product_id": 1})
        if not sample:
            sys.exit("reviews est vide")
        pid = sample["product_id"]
        for name in SORTS:
            plan = json.dumps(db.reviews.find({"product_id": pid}).sort(sort_spec(name)).limit(10).explain(), default=str)
            blocking = '"stage": "SORT"' in plan
            ixscan = '"stage": "IXSCAN"' in plan
            print(f"tri {name:12s} IXSCAN={ixscan} tri_en_memoire={blocking}")


if __name__ == "__main__":
    main()
