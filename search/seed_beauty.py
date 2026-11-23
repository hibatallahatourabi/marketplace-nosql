
from db_config import get_client, DB_NAME
from bson.decimal128 import Decimal128

client = get_client()
db = client[DB_NAME]
products = db["products"]

beauty_products = [
    {
        "product_id": "B001",
        "title": "Hair Chalk Pink",
        "brand": "ColorPop",
        "category": {
            "main": "All Beauty",
            "path": [
                "All Beauty",
                "Hair Care",
                "Hair Chalk"
            ]
        },
        "price": Decimal128("120.00"),
        "rating": {"average": 4.5, "count": 100}
    },
    {
        "product_id": "B002",
        "title": "Hair Shampoo",
        "brand": "L'Oreal",
        "category": {
            "main": "All Beauty",
            "path": [
                "All Beauty",
                "Hair Care",
                "Shampoo"
            ]
        },
        "price": Decimal128("85.00"),
        "rating": {"average": 4.2, "count": 75}
    },
    {
        "product_id": "B003",
        "title": "Face Moisturizer",
        "brand": "CeraVe",
        "category": {
            "main": "All Beauty",
            "path": [
                "All Beauty",
                "Skin Care",
                "Moisturizers"
            ]
        },
        "price": Decimal128("150.00"),
        "rating": {"average": 4.8, "count": 200}
    }
]

for product in beauty_products:
    products.update_one(
        {"product_id": product["product_id"]},
        {"$set": product},
        upsert=True
    )

print("Produits Beauty insérés avec succès !")

for product in products.find(
    {"product_id": {"$in": ["B001", "B002", "B003"]}},
    {"_id": 0}
).sort("product_id", 1):
    print(product["product_id"], "-", product["title"])

client.close()
