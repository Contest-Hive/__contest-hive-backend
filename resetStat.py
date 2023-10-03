from sys import argv
from pymongo import MongoClient
MongoClient(argv[-1])["Projects"]["Contest-Hive"].update_one({"_id": 1}, {"$set": {"past24": 0,"past24api": 0,"past24page": 0}})