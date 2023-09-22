import os
import json
import asyncio
from datetime import datetime

import httpx

# Platforms
from platforms import (
    AtCoder,
    CodeChef,
    CodeForces,
    HackerEarth,
    HackerRank,
    LeetCode,
    Toph,
)


class Contests:
    cachedData = {}
    keywordPlatforms = {
        "1": "atcoder",
        "2": "codechef",
        "3": "codeforces",
        "4": "hackerearth",
        "5": "hackerrank",
        "6": "leetcode",
        "7": "toph"
    }

    platformFuncs = {
        "1": AtCoder,
        "2": CodeChef,
        "3": CodeForces,
        "4": HackerEarth,
        "5": HackerRank,
        "6": LeetCode,
        "7": Toph
    }

    def __init__(self):
        # load cached data in memory
        for i in list(self.keywordPlatforms.values()):
            try:
                with open(f"Data/{i}.json", "r", encoding="utf-8") as f:
                    self.cachedData[i] = json.load(f)["data"]
            except FileNotFoundError:
                print(f"File {i}.json not found")
                print("New file will be created when data is fetched")

    def dumpJson(self, name: str, data: dict):
        if not os.path.exists("Data"):
            os.mkdir("Data")

        with open(f"Data/{name}.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)

    def dumpAllJson(self):
        # First Dump all
        allData = {
            "ok": True,
            "data": self.cachedData,
            "lastUpdated": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
        }
        self.dumpJson("all", allData)

        # Then dump each platform
        for i in self.cachedData:
            data = {
                "ok": True,
                "data": self.cachedData[i],
                "lastUpdated": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
            }
            self.dumpJson(i, data)

        print("Dumped all data to json files")

    async def getAllContests(self):
        ses = httpx.AsyncClient(timeout=None, follow_redirects=1)

        print("Getting all contests...")
        x = [func(ses) for func in self.platformFuncs.values()]
        x = await asyncio.gather(*x, return_exceptions=True)

        y = list(self.keywordPlatforms.values())  # list of platform names

        # if any error occurs, we will use the cached data
        # else we will update the cached data
        for i, j in enumerate(x):
            if isinstance(j, Exception):
                print(f"Error in {y[i]}: {j}")

            else:
                self.cachedData[y[i]] = j
                print(f"Updated {y[i]}")

        self.dumpAllJson()


if __name__ == "__main__":
    c = Contests()
    asyncio.run(c.getAllContests())
