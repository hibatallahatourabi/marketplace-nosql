
from db_config import get_client, DB_NAME
from bson.decimal128 import Decimal128


def validate_product(product):
    errors = []

    required_strings = ["product_id", "title"]

    for field in required_strings:
        value = product.get(field)
        if not isinstance(value, str) or not value.strip():
            errors.append(f"{field} doit etre une chaine non vide")

    brand = product.get("brand")
    if brand is not None and not isinstance(brand, str):
        errors.append("brand doit etre String ou None")

    category = product.get("category")

    if not isinstance(category, dict):
        errors.append("category doit etre un objet")
    else:
        main = category.get("main")
        path = category.get("path")

        if not isinstance(main, str) or not main.strip():
            errors.append("category.main doit etre une chaine non vide")

        if not isinstance(path, list) or not all(
            isinstance(item, str) for item in path
        ):
            errors.append("category.path doit etre Array[String]")
        elif not path or path[0] != main:
            errors.append(
                "category.path doit commencer par category.main"
            )

    # Le membre 1 accepte Decimal128 ou None.
    price = product.get("price")

    if price is not None and not isinstance(price, Decimal128):
        errors.append("price doit etre Decimal128 ou None")

    # Le membre 1 accepte un objet rating vide.
    rating = product.get("rating")

    if not isinstance(rating, dict):
        errors.append("rating doit etre un objet")
    else:
        average = rating.get("average")
        count = rating.get("count")

        if average is not None:
            if (
                isinstance(average, bool)
                or not isinstance(average, (int, float))
            ):
                errors.append("rating.average doit etre numerique")
            elif not 0 <= average <= 5:
                errors.append("rating.average doit etre entre 0 et 5")

        if count is not None:
            if (
                isinstance(count, bool)
                or not isinstance(count, int)
                or count < 0
            ):
                errors.append(
                    "rating.count doit etre un entier positif ou nul"
                )

    return errors


def check_schema():
    client = get_client()

    try:
        db = client[DB_NAME]
        products = db["products"]

        test_ids = ["B001", "B002", "B003"]

        documents = list(products.find({
            "product_id": {"$in": test_ids}
        }))

        print("Produits trouves :", len(documents))

        invalid = 0

        for product in documents:
            product_id = product.get("product_id", "INCONNU")
            errors = validate_product(product)

            if errors:
                invalid += 1
                print(f"\n{product_id} : INVALIDE")
                for error in errors:
                    print(" -", error)
            else:
                print(f"{product_id} : VALIDE")

        missing = set(test_ids) - {
            product.get("product_id") for product in documents
        }

        for product_id in sorted(missing):
            print(f"{product_id} : ABSENT")

        print("\nBilan :")
        print("Produits valides :", len(documents) - invalid)
        print("Produits invalides :", invalid)
        print("Produits absents :", len(missing))

        if invalid or missing:
            raise SystemExit(1)

        print("Validation du schema reussie !")

    finally:
        client.close()


if __name__ == "__main__":
    check_schema()
