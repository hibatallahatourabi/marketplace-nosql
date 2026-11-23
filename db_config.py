
import os
from dotenv import load_dotenv
from pymongo import MongoClient

# Charger les variables du fichier .env
load_dotenv()

# Configuration MongoDB
MONGODB_URI = os.getenv(
    "MONGODB_URI",
    "mongodb://localhost:27017/"
)

DB_NAME = os.getenv("MONGODB_DB", "marketplace_db")


def get_client():
    return MongoClient(
        MONGODB_URI,
        serverSelectionTimeoutMS=5000
    )


def get_database():
    client = get_client()
    return client[DB_NAME]
