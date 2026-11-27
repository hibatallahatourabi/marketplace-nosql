import json
import ijson
from collections import Counter
from pathlib import Path
import time

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

PRODUCTS_FILE = DATA_DIR / "beauty_products_final_5000.json"
MAPPING_FILE = DATA_DIR / "asin2category.json"
OUTPUT_FILE = DATA_DIR / "dataset_origin_results.json"

start = time.perf_counter()

# 1. Charger les 5000 produits
with open(PRODUCTS_FILE, "r", encoding="utf-8") as f:
    products = json.load(f)

product_ids = {p["product_id"] for p in products}

print("=== DATASET PRODUCTS ===")
print("Total products:", len(products))
print("Unique product IDs:", len(product_ids))

# 2. Lire progressivement le fichier officiel
matches = {}
scanned = 0

print("\n=== SCANNING OFFICIAL MAPPING ===")

with open(MAPPING_FILE, "rb") as f:
    for asin, category in ijson.kvitems(f, ""):
        scanned += 1

        if asin in product_ids:
            matches[asin] = category

        if scanned % 5000000 == 0:
            print(
                f"Scanned: {scanned:,} | "
                f"Matches: {len(matches)}/"
                f"{len(product_ids)}",
                flush=True
            )

# 3. Calculer les resultats
missing_ids = sorted(product_ids - matches.keys())
distribution = Counter(matches.values())

match_rate = len(matches) / len(product_ids) * 100

print("\n=== FINAL RESULTS ===")
print("Mapping entries scanned:", scanned)
print("Products analyzed:", len(product_ids))
print("Matched IDs:", len(matches))
print("Unmatched IDs:", len(missing_ids))
print(f"Match rate: {match_rate:.2f}%")

# 4. Afficher les categories sources
print("\n=== SOURCE CATEGORY DISTRIBUTION ===")

for category, count in distribution.most_common():
    percentage = count / len(product_ids) * 100
    print(f"{category}: {count} ({percentage:.2f}%)")

# 5. Comparer les deux categories principales
print("\n=== TARGET CATEGORIES ===")
print(
    "Beauty and Personal Care:",
    distribution.get("Beauty and Personal Care", 0)
)
print(
    "All Beauty:",
    distribution.get("All Beauty", 0)
)

# 6. Sauvegarder les resultats
results = {
    "total_products": len(products),
    "unique_product_ids": len(product_ids),
    "mapping_entries_scanned": scanned,
    "matched_ids": len(matches),
    "unmatched_ids": len(missing_ids),
    "match_rate": round(match_rate, 2),
    "source_categories": dict(distribution),
    "product_source_mapping": matches,
    "missing_product_ids": missing_ids
}

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, ensure_ascii=False)

elapsed = time.perf_counter() - start

print("\nResults saved to:", OUTPUT_FILE)
print(f"Execution time: {elapsed:.2f} seconds")
print("=== ANALYSIS COMPLETED ===")