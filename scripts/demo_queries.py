"""Lance toutes les requetes du Membre 3 sur la base et enregistre les sorties dans un fichier Markdown.

  python scripts/demo_queries.py                       # ecrit docs/sample_outputs.md
  python scripts/demo_queries.py --product-id B00BOJO7ZU --keywords "hair chalk"

Lecture seule : aucune ecriture dans la base (le stock n'est que lu). L'URI de connexion n'est jamais ecrite.
Les temps sont ceux d'UNE execution : indicatifs, ce ne sont pas des benchmarks.
"""
import argparse, json, sys, time
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.db import get_db
from src.queries import products as P, reviews as R
from src.operations.update_stock import get_available

MAX_STR = 160


def shorten(x):
    """Raccourcit les longs textes (reviews, descriptions) pour garder un fichier lisible."""
    if isinstance(x, str):
        return x if len(x) <= MAX_STR else x[:MAX_STR] + "..."
    if isinstance(x, list):
        return [shorten(v) for v in x[:8]] + (["..."] if len(x) > 8 else [])
    if isinstance(x, dict):
        return {k: shorten(v) for k, v in x.items()}
    return x


def run(steps, out):
    for title, call_text, fn in steps:
        t0 = time.perf_counter()
        try:
            result, status = fn(), "ok"
        except Exception as e:                  # une etape en erreur ne bloque pas les autres
            result, status = f"{type(e).__name__}: {e}", "ERREUR"
        ms = (time.perf_counter() - t0) * 1000
        print(f"[{status}] {title}  ({ms:.0f} ms)")
        out.append(f"## {title}\n\n`{call_text}`  \nStatut : {status} - temps indicatif : {ms:.0f} ms\n")
        out.append("```json\n" + json.dumps(shorten(result), indent=2, default=str, ensure_ascii=False) + "\n```\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="docs/sample_outputs.md")
    ap.add_argument("--product-id", default="B00BOJO7ZU")
    ap.add_argument("--keywords", default="hair chalk")
    a = ap.parse_args()

    pid, kw = a.product_id, a.keywords
    hair = ["Beauty & Personal Care", "Hair Care"]
    crit = {"main": "All Beauty", "path": hair, "min_price": 0, "max_price": 100, "min_rating": 4}
    state = {}

    def facet_step():
        state["facets"] = P.facets({"path": hair})
        return state["facets"]

    def brand_rating_step():
        if "facets" in state:
            brand = state["facets"]["brands"][0]["_id"]      # marque la plus frequente des facettes
        else:                                                # facettes en erreur : on prend la marque du produit
            brand = P.find_product_by_id(pid)["brand"]
        r = P.filter_products({"path": hair, "brand": brand, "min_rating": 4}, page_size=3)
        return {"brand": brand, **r}

    def stock_step():
        av = get_available(pid)
        if av is not None:
            return {"product_id": pid, "available": av}
        # ce produit n'a pas de fiche inventory : on prend le premier produit qui en a une
        doc = get_db().inventory.find_one({}, {"_id": 0, "product_id": 1})
        if doc is None:
            return {"product_id": pid, "available": None, "note": "la collection inventory est vide"}
        return {"product_id": doc["product_id"], "available": get_available(doc["product_id"]),
                "note": f"{pid} n'a pas de fiche inventory ; exemple pris sur un produit qui en a une"}

    # ordre d'execution : les facettes (5) passent avant l'etape 4, qui reutilise leur marque la plus frequente
    steps = [
        ("1. Produit par ID", f"find_product_by_id('{pid}')", lambda: P.find_product_by_id(pid)),
        ("2. Recherche par mots-cles", f"search_by_keywords('{kw}', page_size=3)",
         lambda: P.search_by_keywords(kw, page_size=3)),
        ("3. Filtre categorie, prix et note", f"filter_products({crit}, page_size=3)",
         lambda: P.filter_products(crit, page_size=3)),
        ("5. Recherche a facettes (Hair Care)", f"facets({{'path': {hair}}})", facet_step),
        ("4. Filtre marque et note minimale", "filter_products({path, brand: <marque la plus frequente>, min_rating: 4})",
         brand_rating_step),
        ("6a. Categorie et descendants", f"category_with_descendants('All Beauty', {hair})",
         lambda: P.category_with_descendants("All Beauty", hair)[:10]),
        ("6b. Produits de la categorie et sous-categories", f"products_in_category('All Beauty', {hair}, page_size=3)",
         lambda: P.products_in_category("All Beauty", hair, page_size=3)),
        ("7a. Reviews paginees, page 1 (les plus recentes)", f"get_reviews_page('{pid}', page=1, page_size=3)",
         lambda: R.get_reviews_page(pid, page=1, page_size=3)),
        ("7b. Reviews paginees, page 2 (les plus utiles)", f"get_reviews_page('{pid}', page=2, page_size=3, sort='helpful')",
         lambda: R.get_reviews_page(pid, page=2, page_size=3, sort="helpful")),
        ("8. Moyenne et nombre d'avis", f"get_rating_stats('{pid}')", lambda: R.get_rating_stats(pid)),
        ("9. Produit avec ses reviews ($lookup)", f"get_product_with_reviews('{pid}', limit=2)",
         lambda: R.get_product_with_reviews(pid, limit=2)),
        ("10. Stock disponible (lecture seule)", f"get_available('{pid}')", stock_step),
    ]
    final = steps

    db = get_db()
    out = [f"# Sorties d'exemple - requetes du Membre 3\n",
           f"Generees le {datetime.now(timezone.utc):%Y-%m-%d %H:%M} UTC sur la base `{db.name}` "
           f"({db.products.estimated_document_count()} produits, {db.reviews.estimated_document_count()} reviews). "
           "Lecture seule. Textes longs raccourcis. Temps = une seule execution, indicatif.\n"]
    run(final, out)
    path = Path(a.out)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(out), encoding="utf-8")
    print(f"\nEcrit : {path}")


if __name__ == "__main__":
    main()
