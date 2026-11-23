
import pytest
from db_config import get_client, DB_NAME
from bson.decimal128 import Decimal128

from search.product_search import search_products
from search.facet_search import facet_search


@pytest.fixture(scope="module")
def db():
    client = get_client()
    client.admin.command("ping")
    database = client[DB_NAME]
    yield database
    client.close()


def test_search_by_category():
    results = search_products(
        category="All Beauty"
    )

    ids = {p["product_id"] for p in results}

    assert {"B001", "B002", "B003"}.issubset(ids)


def test_search_by_brand():
    results = search_products(
        brand="CeraVe",
        category="All Beauty"
    )

    assert any(p["product_id"] == "B003" for p in results)


def test_search_by_price_and_rating():
    results = search_products(
        min_price=80,
        max_price=130,
        min_rating=4.0,
        category="All Beauty",
        subcategory="Hair Care"
    )

    ids = {p["product_id"] for p in results}

    assert {"B001", "B002"}.issubset(ids)
    assert "B003" not in ids


def test_price_type(db):
    product = db["products"].find_one(
        {"product_id": "B001"}
    )

    assert product is not None
    assert isinstance(product["price"], Decimal128)


def test_facet_search():
    results = facet_search("All Beauty")

    assert len(results) == 1

    facets = results[0]

    assert "brands" in facets
    assert "price_ranges" in facets
    assert "ratings" in facets

    brand_counts = {
        item["_id"]: item["count"]
        for item in facets["brands"]
    }

    assert brand_counts.get("ColorPop", 0) >= 1
    assert brand_counts.get("CeraVe", 0) >= 1
