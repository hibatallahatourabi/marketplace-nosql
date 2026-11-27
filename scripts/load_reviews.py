"""Charge les reviews Amazon (JSONL) dans `reviews`, uniquement pour les produits du dataset final.

Les IDs de produits viennent du fichier local beauty_products_final_5000.json (--ids-file),
donc le script ne depend plus de l'etat de `products` dans Atlas.

Exemples:
  # 1) Test a blanc : ne touche pas a Atlas, affiche juste les compteurs
  python scripts/load_reviews.py data/All_Beauty.jsonl --ids-file data/beauty_products_final_5000.json --dry-run

  # 2) Petit test (10000 premieres lignes) puis import reel
  python scripts/load_reviews.py data/All_Beauty.jsonl --ids-file data/beauty_products_final_5000.json --max-lines 10000
  python scripts/load_reviews.py data/All_Beauty.jsonl --ids-file data/beauty_products_final_5000.json --max-per-product 20
"""
import argparse, gzip, json, re, sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


PARENT_RE = re.compile(r'"parent_asin": ?"([^"]+)"')
ASIN_RE = re.compile(r'"asin": ?"([^"]+)"')


def load_ids(path):
    """Lit les product_id depuis un JSON (liste) ou un JSONL."""
    p = Path(path)
    with open(p, encoding="utf-8") as f:
        text = f.read()
    try:
        data = json.loads(text)
        rows = data if isinstance(data, list) else [data]
    except ValueError:  # JSON Lines
        rows = [json.loads(l) for l in text.splitlines() if l.strip()]
    return {r["product_id"] for r in rows if r.get("product_id")}


def convert(raw):
    ts = raw.get("timestamp")
    return {
        "product_id": raw.get("parent_asin") or raw.get("asin"),
        "_asin": raw.get("asin"),
        "user_id": raw.get("user_id"),
        "rating": float(raw["rating"]) if raw.get("rating") is not None else None,
        "title": raw.get("title"),
        "text": raw.get("text"),
        "helpful_vote": int(raw.get("helpful_vote") or 0),
        "verified_purchase": bool(raw.get("verified_purchase", False)),
        "created_at": datetime.fromtimestamp(ts / 1000, tz=timezone.utc) if ts else None,
    }


def iter_reviews(jsonl_path, known, max_per_product, max_lines=None, stats=None):
    """Genere les reviews valides. `stats` (dict) est rempli meme si rien n'est garde."""
    stats = stats if stats is not None else defaultdict(int)
    counts = defaultdict(int)
    path = str(jsonl_path)
    opener = gzip.open if path.endswith(".gz") else open  # lit aussi les .jsonl.gz
    with opener(path, "rt", encoding="utf-8", errors="replace") as f:
        for i, line in enumerate(f):
            if max_lines and i >= max_lines:
                break
            stats["lignes_lues"] += 1
            if stats["lignes_lues"] % 1_000_000 == 0:
                print(f"  ... {stats['lignes_lues']:,} lignes lues, {stats['gardees']:,} gardees", flush=True)
            # Chemin rapide : on evite json.loads si ni parent_asin ni asin ne sont dans le dataset
            mp, ma = PARENT_RE.search(line), ASIN_RE.search(line)
            if mp and mp.group(1) not in known and not (ma and ma.group(1) in known):
                stats["hors_dataset"] += 1
                continue
            try:
                r = convert(json.loads(line))
            except (ValueError, KeyError, TypeError):
                stats["invalides"] += 1
                continue
            pid = r["product_id"]
            if pid not in known and r.get("_asin") in known:
                pid = r["product_id"] = r["_asin"]  # le dataset utilise l'asin, pas le parent_asin
                stats["match_par_asin"] += 1
            r.pop("_asin", None)
            if pid not in known:
                stats["hors_dataset"] += 1
                if "exemple_id_review" not in stats:
                    stats["exemple_id_review"] = pid
                continue
            if r["rating"] is None:
                stats["invalides"] += 1
                continue
            if counts[pid] >= max_per_product:
                stats["au_dela_du_plafond"] += 1
                continue
            counts[pid] += 1
            stats["gardees"] += 1
            yield r, stats
    stats["produits_avec_reviews"] = len(counts)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("jsonl")
    ap.add_argument("--ids-file", required=True, help="beauty_products_final_5000.json")
    ap.add_argument("--max-per-product", type=int, default=20)
    ap.add_argument("--max-lines", type=int, default=None)
    ap.add_argument("--batch", type=int, default=1000)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--reset", action="store_true",
                    help="vide la collection reviews avant l'import (evite les doublons)")
    a = ap.parse_args()

    known = load_ids(a.ids_file)
    print(f"{len(known)} produits dans le dataset final")

    db = None
    if not a.dry_run:
        from pymongo import ASCENDING, DESCENDING
        from src.db import get_db
        db = get_db()
        existing = db.reviews.estimated_document_count()
        if existing and not a.reset:
            sys.exit(f"STOP : `reviews` contient deja {existing} documents. "
                     "Relance avec --reset pour repartir de zero (sinon doublons).")
        if a.reset:
            db.reviews.delete_many({})
            print("collection reviews videe")

    batch, stats, inserted = [], defaultdict(int), 0
    for r, _ in iter_reviews(a.jsonl, known, a.max_per_product, a.max_lines, stats):
        if db is not None:
            batch.append(r)
            if len(batch) >= a.batch:
                db.reviews.insert_many(batch, ordered=False)
                inserted += len(batch)
                batch = []
                if inserted % (a.batch * 10) == 0:
                    print(f"  >>> {inserted:,} reviews inserees dans Atlas", flush=True)
    if db is not None and batch:
        db.reviews.insert_many(batch, ordered=False)

    if db is not None:
        db.reviews.create_index([("product_id", ASCENDING), ("created_at", DESCENDING)])
        db.reviews.create_index([("product_id", ASCENDING), ("rating", DESCENDING)])
    print(dict(stats), "(dry-run, rien ecrit)" if a.dry_run else "")
    if not stats.get("gardees"):
        print("ATTENTION : 0 review gardee. exemple d'ID produit dans le dataset:", next(iter(known)))


if __name__ == "__main__":
    main()
