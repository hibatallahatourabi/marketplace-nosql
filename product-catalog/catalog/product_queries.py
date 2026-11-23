
def find_products_by_category(collection, category):
    return list(collection.find({
        "category.path": category
    }, {"_id": 0}))


def find_products_by_brand(collection, brand):
    return list(collection.find({
        "brand": {
            "$regex": brand,
            "$options": "i"
        }
    }, {"_id": 0}))


def find_products_by_attribute(collection, attribute, value):
    return list(collection.find({
        f"attributes.{attribute}": {
            "$regex": str(value),
            "$options": "i"
        }
    }, {"_id": 0}))
