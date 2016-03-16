__author__ = 'kanhua'

import json
import codecs
from pymongo import MongoClient
from pymongo import cursor

def test_db(db):

    khh=db.khh

    print(khh.find_one())


def easy_queries(db):

    khh=db.khh
    print(khh.find({"type":"node"}).count())
    print(khh.find({"type":"way"}).count())
    assert isinstance('type',str)
    print(len(khh.distinct('created.user')))

if __name__ == "__main__":
    # Code here is for local use on your own computer.

    client = MongoClient("mongodb://localhost:27017")
    db = client.osm
    easy_queries(db)


