"""Cree les index de `reviews` et `inventory` (sans reimporter) et verifie qu'ils servent les tris.

  python scripts/ensure_indexes.py            # cree / met a jour les index
  python scripts/ensure_indexes.py --explain  # + verifie chaque tri avec explain()
"""
import argparse, sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.db import get_db
from src.operations.indexes import ensure_review_indexes, ensure_inventory_unique_index, ensure_products_text_index, explain_summary, products_storage
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
        before = products_storage(db)
        print("products AVANT :", before or "collStats indisponible : regarde la taille dans Compass")
        print("products (texte) :", ensure_products_text_index(db))
        after = products_storage(db)
        print("products APRES :", after or "collStats indisponible : regarde la taille dans Compass")
        if before and after:
            print("index ajoutes (Mo) :", round(after["index_total_mo"] - before["index_total_mo"], 3))

    if a.explain:
        sample = db.reviews.find_one({}, {"product_id": 1})
        if not sample:
            sys.exit("reviews est vide")
        pid = sample["product_id"]
        for name in SORTS:
            plan = db.reviews.find({"product_id": pid}).sort(sort_spec(name)).limit(10).explain()
            stages, indexes = explain_summary(plan)
            print(f"tri {name:12s} index={indexes} etapes={stages} tri_en_memoire={'SORT' in stages}")

if __name__ == "__main__":
    main()
