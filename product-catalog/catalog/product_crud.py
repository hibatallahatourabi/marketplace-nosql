
def create_product(collection, product):
    result = collection.insert_one(product)
    return result.inserted_id


def get_product_by_id(collection, product_id):
    return collection.find_one(
        {"product_id": product_id},
        {"_id": 0}
    )


def update_product(collection, product_id, updates):
    return collection.update_one(
        {"product_id": product_id},
        {"$set": updates}
    )


def delete_product(collection, product_id):
    return collection.delete_one(
        {"product_id": product_id}
    )


def list_products(collection, page=1, page_size=10):
    if page < 1 or page_size < 1:
        raise ValueError("Page and page_size must be positive.")

    skip = (page - 1) * page_size

    result = list(
        collection.find({}, {"_id": 0})
        .sort("product_id", 1)
        .skip(skip)
        .limit(page_size)
    )

    return result
