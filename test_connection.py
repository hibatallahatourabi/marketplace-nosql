
from pymongo import MongoClient

client = MongoClient(
    "mongodb://localhost:27017/",
    serverSelectionTimeoutMS=5000
)

try:
    client.admin.command("ping")

    db = client["marketplace_nosql"]

    print("Connexion MongoDB réussie !")
    print("Base de données :", db.name)
    print("Collections :", db.list_collection_names())

except Exception as e:
    print("Erreur de connexion :", e)

finally:
    client.close()
