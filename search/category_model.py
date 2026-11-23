
from db_config import get_client, DB_NAME


def create_categories():
    client = get_client()

    try:
        db = client[DB_NAME]
        categories = db["categories"]

        data = [
            {
                "category_id": "beauty",
                "name": "All Beauty",
                "parent_id": None,
                "ancestors": []
            },
            {
                "category_id": "hair_care",
                "name": "Hair Care",
                "parent_id": "beauty",
                "ancestors": ["beauty"]
            },
            {
                "category_id": "hair_chalk",
                "name": "Hair Chalk",
                "parent_id": "hair_care",
                "ancestors": ["beauty", "hair_care"]
            },
            {
                "category_id": "shampoo",
                "name": "Shampoo",
                "parent_id": "hair_care",
                "ancestors": ["beauty", "hair_care"]
            },
            {
                "category_id": "skin_care",
                "name": "Skin Care",
                "parent_id": "beauty",
                "ancestors": ["beauty"]
            },
            {
                "category_id": "moisturizers",
                "name": "Moisturizers",
                "parent_id": "skin_care",
                "ancestors": ["beauty", "skin_care"]
            }
        ]

        categories.create_index(
            "category_id",
            unique=True
        )

        for category in data:
            categories.update_one(
                {"category_id": category["category_id"]},
                {"$set": category},
                upsert=True
            )

        print("Catégories enregistrées avec succès !")
        print("Nombre de catégories de test :", len(data))

        for category in categories.find(
            {"category_id": {"$in": [c["category_id"] for c in data]}},
            {"_id": 0}
        ).sort("category_id", 1):
            print(category)

    finally:
        client.close()


if __name__ == "__main__":
    create_categories()
