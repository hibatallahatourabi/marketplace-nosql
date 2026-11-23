
from db_config import get_client, DB_NAME
from search.product_search import search_products


def test_search_with_missing_values():
    client = get_client()
    products = client[DB_NAME]["products"]

    test_id = "TEST_SEARCH_MISSING"

    product = {
        "product_id": test_id,
        "title": "Temporary Search Product",
        "brand": "Test Brand",
        "category": {
            "main": "All Beauty",
            "path": ["All Beauty", "Hair Care"]
        },
        "price": None,
        "rating": {}
    }

    try:
        products.replace_one(
            {"product_id": test_id},
            product,
            upsert=True
        )

        # Sans filtre de prix ou de note
        results = search_products(category="All Beauty")
        ids = {p["product_id"] for p in results}
        assert test_id in ids

        # Avec un prix minimum
        results = search_products(
            category="All Beauty",
            min_price=50
        )
        ids = {p["product_id"] for p in results}
        assert test_id not in ids

        # Avec une note minimum
        results = search_products(
            category="All Beauty",
            min_rating=4
        )
        ids = {p["product_id"] for p in results}
        assert test_id not in ids

        # Recherche par sous-categorie
        results = search_products(
            subcategory="Hair Care"
        )
        ids = {p["product_id"] for p in results}
        assert test_id in ids

    finally:
        products.delete_one({"product_id": test_id})
        client.close()
