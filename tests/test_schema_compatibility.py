
from bson.decimal128 import Decimal128
from check_schema import validate_product


def make_product(price, rating):
    return {
        "product_id": "TEST001",
        "title": "Test Product",
        "brand": "Test Brand",
        "category": {
            "main": "All Beauty",
            "path": ["All Beauty", "Hair Care"]
        },
        "price": price,
        "rating": rating
    }


def test_product_without_price():
    product = make_product(None, {
        "average": 4.5,
        "count": 10
    })

    assert validate_product(product) == []


def test_product_without_rating():
    product = make_product(Decimal128("99.00"), {})

    assert validate_product(product) == []


def test_product_without_price_and_rating():
    product = make_product(None, {})

    assert validate_product(product) == []


def test_invalid_price_type():
    product = make_product(99.00, {})

    assert "price doit etre Decimal128 ou None" in validate_product(product)
