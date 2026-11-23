
from db_config import get_client, DB_NAME
from pprint import pprint



def benchmark_search():
    client = get_client()

    try:
        db = client[DB_NAME]
        products = db["products"]

        query = {
            "category.main": "All Beauty"
        }

        print("Nombre de produits :", products.count_documents(query))

        # Recherche utilisant l'index
        indexed = db.command(
            "explain",
            {
                "find": "products",
                "filter": query,
                "hint": "idx_category_main"
            },
            verbosity="executionStats"
        )

        # Recherche sans index (parcours complet)
        collection_scan = db.command(
            "explain",
            {
                "find": "products",
                "filter": query,
                "hint": {"$natural": 1}
            },
            verbosity="executionStats"
        )

        def show_results(name, result):
            stats = result["executionStats"]

            print("\n---", name, "---")
            print("Documents retournés :", stats["nReturned"])
            print("Documents examinés :", stats["totalDocsExamined"])
            print("Clés examinées :", stats["totalKeysExamined"])
            print("Temps d'exécution (ms) :",
                  stats["executionTimeMillis"])

            print("Plan d'exécution :")
            pprint(result["queryPlanner"]["winningPlan"])

        show_results("AVEC INDEX", indexed)
        show_results("SANS INDEX - COLLSCAN", collection_scan)

    finally:
        client.close()


if __name__ == "__main__":
    benchmark_search()
