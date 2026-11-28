# Member 3 - Queries, reviews and stock: how to use

## Setup
1. `pip install -r requirements.txt` (tests: `pip install -r requirements-dev.txt`)
2. Copy `.env.example` to `.env` and set `MONGO_URI` (Atlas connection string). `.env` is never committed.
3. `PRODUCT_KEY=product_id` and `DB_NAME=marketplace_db` are the defaults.

## Code map
| File | Purpose |
| --- | --- |
| `src/db.py` | MongoDB connection (reads `.env`) |
| `src/queries/products.py` | Product by ID, keyword search, filters, facets, category tree and products |
| `src/queries/reviews.py` | Paginated reviews, rating statistics, product with reviews (`$lookup`) |
| `src/operations/update_stock.py` | Stock: available, increase, reserve, confirm sale |
| `src/operations/indexes.py` | Index helpers for `reviews`, `inventory` and the products text index; `explain()` reader |
| `scripts/load_reviews.py` | Imports reviews for the 5,000 catalogue products |
| `scripts/ensure_indexes.py` | Creates the indexes and checks the sort plans |
| `scripts/demo_queries.py` | Runs every query and writes `docs/sample_outputs.md` |

## Commands
Import reviews (reads the `.gz` directly; run a dry run first):
```
python scripts/load_reviews.py data/Beauty_and_Personal_Care.jsonl.gz --ids-file data/beauty_products_final_5000.json --dry-run
python -u scripts/load_reviews.py data/Beauty_and_Personal_Care.jsonl.gz --ids-file data/beauty_products_final_5000.json --max-per-product 20 --reset
```
`--reset` empties `reviews` first; without it the script refuses to run on a non-empty collection.

Indexes:
```
python scripts/ensure_indexes.py --explain      # review indexes, inventory index check, sort plans
python scripts/ensure_indexes.py --text-index   # products text index idx_product_text, with storage before/after
```

Sample outputs and tests:
```
python scripts/demo_queries.py
python -m pytest -q tests
```

## Notes
- `rating.count` in `products` is Amazon's total. Review statistics come from the `reviews` collection, which holds a sample (at most 20 reviews per product).
- Without the text index, keyword search falls back to a title match where all words must appear. With it, any word matches and results are ranked by relevance.
- Offline tests use a simulated MongoDB that cannot compare `Decimal128` prices; price filters and facets are verified on Atlas.
- Data files (`data/`) and `.env` are never committed.
