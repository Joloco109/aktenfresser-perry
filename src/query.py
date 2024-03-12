import re

from pymongo import MongoClient

if __name__ == "__main__":

    CONNECTION_STRING = "mongodb://root:example@localhost"

    QUERY_STRING = "O 127/23"

    client = MongoClient(CONNECTION_STRING)
    db = client["Gerichtstermine"]

    col = db["LG Aachen"]

    results = col.find({"termine.aktenzeichen": {"$regex": f"{QUERY_STRING}"}})

    for result in results:
        for termin in result["termine"]:
            if re.match(QUERY_STRING, termin["aktenzeichen"]) is not None:
                print(termin)
