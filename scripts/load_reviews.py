"""Charge les reviews Amazon (JSONL) dans `reviews`, uniquement pour les produits deja presents.

Usage:
  python scripts/load_reviews.py data/All_Beauty.jsonl --max-per-product 30
"""
import argparse, json, sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from pymongo import ASCENDING, DESCENDING
from src.db import get_db, PRODUCT_KEY


def convert(raw):
    ts = raw.get("timestamp")
    return {
        "product_id": raw.get("parent_asin") or raw.get("asin"),
        "user_id": raw.get("user_id"),
        "rating": float(raw["rating"]) if raw.get("rating") is not None else None,
        "title": raw.get("title"),
        "text": raw.get("text"),
        "helpful_vote": int(raw.get("helpful_vote") or 0),
        "verified_purchase": bool(raw.get("verified_purchase", False)),
        "created_at": datetime.fromtimestamp(ts / 1000, tz=timezone.utc) if ts else None,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("jsonl")
    ap.add_argument("--max-per-product", type=int, default=30)
    ap.add_argument("--batch", type=int, default=1000)
    a = ap.parse_args()

    db = get_db()
    known = {d[PRODUCT_KEY] for d in db.products.find({}, {PRODUCT_KEY: 1}) if PRODUCT_KEY in d}
    print(f"{len(known)} produits connus")
    counts, batch, kept, orphan, bad = defaultdict(int), [], 0, 0, 0

    with open(a.jsonl, encoding="utf-8") as f:
        for line in f:
            try:
                r = convert(json.loads(line))
            except (ValueError, KeyError):
                bad += 1; continue
            pid = r["product_id"]
            if pid not in known: orphan += 1; continue
            if r["rating"] is None or counts[pid] >= a.max_per_product: continue
            counts[pid] += 1; batch.append(r); kept += 1
            if len(batch) >= a.batch:
                db.reviews.insert_many(batch, ordered=False); batch = []
    if batch: db.reviews.insert_many(batch, ordered=False)

    db.reviews.create_index([("product_id", ASCENDING), ("created_at", DESCENDING)])
    db.reviews.create_index([("product_id", ASCENDING), ("rating", DESCENDING)])
    print(f"inserees={kept} orphelines_ignorees={orphan} invalides={bad}")


if __name__ == "__main__":
    main()
