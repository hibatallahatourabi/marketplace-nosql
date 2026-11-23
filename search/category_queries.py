
from db_config import get_client, DB_NAME



def get_direct_subcategories(categories, category_id):
    return list(categories.find(
        {"parent_id": category_id},
        {"_id": 0}
    ))


def get_all_descendants(categories, category_id):
    return list(categories.find(
        {"ancestors": category_id},
        {"_id": 0}
    ))


def get_products_in_hierarchy(db, category_id):
    categories = db["categories"]
    products = db["products"]

    root = categories.find_one(
        {"category_id": category_id},
        {"_id": 0}
    )

    if root is None:
        return []

    descendants = get_all_descendants(
        categories, category_id
    )

    names = [root["name"]]
    names.extend(cat["name"] for cat in descendants)

    return list(products.find(
        {"category.path": {"$in": names}},
        {"_id": 0}
    ))


if __name__ == "__main__":
    client = get_client()

    try:
        db = client[DB_NAME]
        categories = db["categories"]

        print("\n1. Sous-categories directes de Beauty :")
        direct = get_direct_subcategories(
            categories, "beauty"
        )

        for category in direct:
            print("-", category["name"])

        print("\n2. Tous les descendants de Beauty :")
        descendants = get_all_descendants(
            categories, "beauty"
        )

        for category in descendants:
            print("-", category["name"])

        print("\n3. Produits de Hair Care et descendants :")
        results = get_products_in_hierarchy(
            db, "hair_care"
        )

        print("Nombre de produits :", len(results))

        for product in results:
            print(
                product["product_id"],
                "-",
                product["title"]
            )

    finally:
        client.close()
