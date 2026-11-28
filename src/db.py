"""Connexion MongoDB partagee. Les secrets viennent de .env (jamais commite)."""
import os
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

PRODUCT_KEY = os.getenv("PRODUCT_KEY", "product_id")  # cle produit dans `products`
_client = None


def get_db():
    global _client
    if _client is None:
        uri = os.environ["MONGO_URI"]
        _client = MongoClient(uri, serverSelectionTimeoutMS=8000)
    return _client[os.getenv("DB_NAME", "marketplace_db")]
