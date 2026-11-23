
from db_config import get_client, DB_NAME
from search.facet_search import facet_search


def test_facet_with_missing_values():
    client = get_client()
    products = client[DB_NAME]["products"]

    test_id = "TEST_FACET_MISSING"

    product = {
        "product_id": test_id,
        "title": "Temporary Test Product",
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

        result = facet_search("All Beauty")[0]

        price_counts = {
            str(item["_id"]): item["count"]
            for item in result["price_ranges"]
        }

        rating_counts = {
            item["_id"]: item["count"]
            for item in result["ratings"]
        }

        assert price_counts.get("Other or Missing", 0) >= 1
        assert rating_counts.get("Other or Missing", 0) >= 1

    finally:
        products.delete_one({"product_id": test_id})
        client.close()
