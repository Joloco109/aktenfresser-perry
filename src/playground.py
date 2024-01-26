from dataclasses import asdict
from pymongo import MongoClient
from tqdm import tqdm
from scraper import Scraper

GERICHTE = []

if __name__ == "__main__":

    # Load All NRW Gerichte form file

    with open("gerichte_nrw.txt", "r") as gerichte_provider:
        for line in gerichte_provider:
            GERICHTE.append(line.replace("ü", "ue").replace("ä", "ae").replace("ö", "oe").rstrip())

    # Provide the mongodb atlas url to connect python to mongodb using pymongo
    CONNECTION_STRING = "mongodb://root:example@localhost"
    client = MongoClient(CONNECTION_STRING)
    db = client["Gerichtstermine"]

    for gericht in tqdm(GERICHTE):
        scraper = Scraper(gericht)
        scrape = scraper.update()

        collection = db[gericht]

        json_termine = asdict(scrape)
        collection.insert_one(json_termine)

