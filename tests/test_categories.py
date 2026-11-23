
import pytest
from db_config import get_client, DB_NAME

from search.category_queries import (
    get_direct_subcategories,
    get_all_descendants,
    get_products_in_hierarchy
)


@pytest.fixture(scope="module")
def db():
    client = get_client()
    client.admin.command("ping")
    database = client[DB_NAME]
    yield database
    client.close()


def test_direct_subcategories(db):
    results = get_direct_subcategories(
        db["categories"], "beauty"
    )

    names = {c["name"] for c in results}

    assert "Hair Care" in names
    assert "Skin Care" in names


def test_all_descendants(db):
    results = get_all_descendants(
        db["categories"], "beauty"
    )

    names = {c["name"] for c in results}

    assert {
        "Hair Care",
        "Hair Chalk",
        "Shampoo",
        "Skin Care",
        "Moisturizers"
    }.issubset(names)


def test_hair_care_products(db):
    results = get_products_in_hierarchy(
        db, "hair_care"
    )

    ids = {p["product_id"] for p in results}

    assert {"B001", "B002"}.issubset(ids)
    assert "B003" not in ids


def test_unknown_category(db):
    results = get_products_in_hierarchy(
        db, "unknown_category"
    )

    assert results == []


def test_category_parent(db):
    category = db["categories"].find_one(
        {"category_id": "hair_chalk"}
    )

    assert category is not None
    assert category["parent_id"] == "hair_care"
    assert category["ancestors"] == [
        "beauty",
        "hair_care"
    ]
