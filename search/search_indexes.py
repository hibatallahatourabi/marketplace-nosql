
from pymongo import ASCENDING, DESCENDING
from db_config import get_client, DB_NAME



def create_search_indexes():
    client = get_client()

    try:
        db = client[DB_NAME]

        products = db["products"]
        categories = db["categories"]

        print("Création des index de recherche...\n")

        product_indexes = [
            ("idx_brand", [("brand", ASCENDING)]),
            ("idx_price", [("price", ASCENDING)]),
            ("idx_rating", [("rating.average", DESCENDING)]),
            ("idx_category_main", [("category.main", ASCENDING)]),
            ("idx_category_path", [("category.path", ASCENDING)]),
            (
                "idx_category_price_rating",
                [
                    ("category.main", ASCENDING),
                    ("price", ASCENDING),
                    ("rating.average", DESCENDING)
                ]
            )
        ]

        for name, keys in product_indexes:
            products.create_index(keys, name=name)
            print("Index products créé :", name)

        category_indexes = [
            ("idx_parent_id", [("parent_id", ASCENDING)]),
            ("idx_ancestors", [("ancestors", ASCENDING)])
        ]

        for name, keys in category_indexes:
            categories.create_index(keys, name=name)
            print("Index categories créé :", name)

        print("\nIndex de la collection products :")
        for name in products.index_information():
            print("-", name)

        print("\nIndex de la collection categories :")
        for name in categories.index_information():
            print("-", name)

        print("\nCréation des index terminée !")

    finally:
        client.close()


if __name__ == "__main__":
    create_search_indexes()
