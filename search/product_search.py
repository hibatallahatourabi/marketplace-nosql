
from db_config import get_client, DB_NAME
from bson.decimal128 import Decimal128


def search_products(
    brand=None,
    min_price=None,
    max_price=None,
    min_rating=None,
    category=None,
    subcategory=None
):
    client = get_client()

    try:
        db = client[DB_NAME]
        products = db["products"]

        query = {}

        if brand:
            query["brand"] = brand

        if min_price is not None or max_price is not None:
            query["price"] = {}

            if min_price is not None:
                query["price"]["$gte"] = Decimal128(str(min_price))

            if max_price is not None:
                query["price"]["$lte"] = Decimal128(str(max_price))

        if min_rating is not None:
            query["rating.average"] = {"$gte": min_rating}

        if category:
            query["category.main"] = category

        if subcategory:
            query["category.path"] = subcategory

        return list(products.find(query, {"_id": 0}))

    finally:
        client.close()


if __name__ == "__main__":

    results = search_products(
        min_price=80,
        max_price=130,
        min_rating=4.0,
        subcategory="Hair Care"
    )

    print("Produits trouves :", len(results))

    for product in results:
        print(
            product["product_id"],
            "-",
            product["title"],
            "-",
            product.get("price")
        )
