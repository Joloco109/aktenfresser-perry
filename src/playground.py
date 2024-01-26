from dataclasses import asdict
from bson import json_util
import json
from pymongo import MongoClient

from src.scraper import Scraper

if __name__ == "__main__":
    scraper = Scraper()
    scrape = scraper.update()

    # Provide the mongodb atlas url to connect python to mongodb using pymongo
    CONNECTION_STRING = "mongodb://root:example@localhost"

    # Create a connection using MongoClient. You can import MongoClient or use pymongo.MongoClient
    client = MongoClient(CONNECTION_STRING)
    db = client["Gerichtstermine"]
    collection = db["LG Aachen"]

    json_termine = asdict(scrape)

    print(json_termine)

    collection.insert_one(json_termine)
