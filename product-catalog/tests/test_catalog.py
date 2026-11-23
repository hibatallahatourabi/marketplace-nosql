
import unittest
from unittest.mock import MagicMock

from catalog.product_crud import (
    create_product,
    get_product_by_id,
    update_product,
    delete_product,
    list_products
)

from catalog.product_queries import (
    find_products_by_category,
    find_products_by_brand,
    find_products_by_attribute
)


class TestProductCatalog(unittest.TestCase):

    def setUp(self):
        self.collection = MagicMock()

    def test_create_product(self):
        self.collection.insert_one.return_value.inserted_id = "test123"

        result = create_product(
            self.collection,
            {"product_id": "TEST001", "title": "Test Product"}
        )

        self.assertEqual(result, "test123")

    def test_get_product_by_id(self):
        self.collection.find_one.return_value = {
            "product_id": "TEST001"
        }

        result = get_product_by_id(self.collection, "TEST001")

        self.assertEqual(result["product_id"], "TEST001")

    def test_update_product(self):
        result = update_product(
            self.collection,
            "TEST001",
            {"brand": "Updated Brand"}
        )

        self.collection.update_one.assert_called_once()

    def test_delete_product(self):
        delete_product(self.collection, "TEST001")

        self.collection.delete_one.assert_called_once()

    def test_list_products(self):
        self.collection.find.return_value.sort.return_value.skip.return_value.limit.return_value = [
            {"product_id": "TEST001"}
        ]

        result = list_products(self.collection, page=1, page_size=10)

        self.assertEqual(len(result), 1)

    def test_find_by_category(self):
        find_products_by_category(self.collection, "Hair Care")
        self.collection.find.assert_called_once()

    def test_find_by_brand(self):
        find_products_by_brand(self.collection, "Ebbfurln")
        self.collection.find.assert_called_once()

    def test_find_by_attribute(self):
        find_products_by_attribute(self.collection, "Color", "White")
        self.collection.find.assert_called_once()


if __name__ == "__main__":
    unittest.main(argv=["first-arg-is-ignored"], exit=False)
