
from pprint import pprint
from db_config import get_client, DB_NAME
from bson.decimal128 import Decimal128


def facet_search(category="All Beauty"):
    client = get_client()

    try:
        products = client[DB_NAME]["products"]

        pipeline = [
            {
                "$match": {
                    "category.main": category
                }
            },
            {
                "$facet": {
                    "brands": [
                        {
                            "$group": {
                                "_id": "$brand",
                                "count": {"$sum": 1}
                            }
                        },
                        {
                            "$sort": {
                                "count": -1,
                                "_id": 1
                            }
                        }
                    ],
                    "price_ranges": [
                        {
                            "$bucket": {
                                "groupBy": {
    "$ifNull": ["$price", "Missing"]
},
                                "boundaries": [
                                    Decimal128("0"),
                                    Decimal128("100"),
                                    Decimal128("200"),
                                    Decimal128("500"),
                                    Decimal128("1000000")
                                ],
                                "default": "Other or Missing",
                                "output": {
                                    "count": {"$sum": 1}
                                }
                            }
                        }
                    ],
                    "ratings": [
                        {
                            "$bucket": {
                                "groupBy": {
    "$ifNull": ["$rating.average", "Missing"]
},
                                "boundaries": [0, 2, 3, 4, 5, 6],
                                "default": "Other or Missing",
                                "output": {
                                    "count": {"$sum": 1}
                                }
                            }
                        }
                    ]
                }
            }
        ]

        return list(products.aggregate(pipeline))

    finally:
        client.close()


if __name__ == "__main__":
    print("Recherche à facettes - All Beauty")
    pprint(facet_search())
