
def create_product_indexes(collection):
    indexes = {}

    indexes["product_id"] = collection.create_index(
        [("product_id", 1)],
        unique=True
    )

    indexes["brand"] = collection.create_index(
        [("brand", 1)]
    )

    indexes["category"] = collection.create_index(
        [("category.path", 1)]
    )

    return indexes
