"""
This script updates the daily statistics and resets the daily statistics to 0.

"""

import os
from sys import argv
from dotenv import load_dotenv
from pymongo import MongoClient
from datetime import datetime, timezone, timedelta

load_dotenv()

MongoURI = argv[-1]

if len(argv) < 2:
    MongoURI = os.environ.get("MongoURI")
    print("Using the default MongoDB URI from .env file")

db = MongoClient(MongoURI)["Projects"]
utcDate = datetime.now(timezone.utc).strftime("%Y-%m-%d")  # 2024-08-23

# check if the date is already in the database
if db["daily-stats"].find_one({"_id": utcDate}):
    print("Adding to the next date.")
    # add to the next day
    # utcDate = (datetime.now(timezone.utc) + timedelta(days=1)).strftime("%Y-%m-%d")


# get the current statistics
stats = db["contest-hive"].find_one({"_id": 1})
# update the daily statistics
db["daily-stats"].update_one(
    {"_id": utcDate},
    {
        "$set": {
            "past24api": stats["past24api"],
            "past24page": stats["past24page"],
        }
    },
    upsert=True,
)

# reset the daily statistics
db["contest-hive"].update_one(
    {"_id": 1}, {"$set": {"past24": 1, "past24api": 1, "past24page": 2}}
)

print(f"Reset the daily statistics for {utcDate}.")
print(f"past24api: {stats['past24api']}")
print(f"past24page: {stats['past24page']}")
