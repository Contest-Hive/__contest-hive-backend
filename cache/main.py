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
    Toph
)


HTTPX_CLIENT = httpx.AsyncClient(timeout=None, follow_redirects=1)


description = """
<h1>Contest Hive 🚀 is an asynchronous API that gives info about upcoming contests from 7 different platforms</h1>

Author: <a href="https://nusab19.pages.dev">Nusab Taha</a>
"""


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
        pass

    def dumpJson(self, name: str, data: dict):
        with open(f"Data/{name}.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4,  ensure_ascii=False)

    async def dumpContests(self, data):
        # making `Data` folder if not exists
        if not os.path.exists("Data"):os.mkdir("Data")

        self.dumpJson("all", data)
        print("Dumped All")
        
        # Dumping each platform
        for name, dt in data["data"].items():
            newData = {
                "ok": True,
                "data": dt,
                "lastUpdated": datetime.now().strftime("%d-%m-%Y %H:%M:%S UTC")
            }
            self.dumpJson(name, newData)
            print(f"Dumped {name}")

        print("Task Finished...")

    async def getAllContests(self):
        x = [func(HTTPX_CLIENT) for func in self.platformFuncs.values()]
        print("Getting all contests")

        x = await asyncio.gather(*x)
        y = self.keywordPlatforms.values()

        data = {
            "ok": True,
            "data": dict(zip(y, x)),
            "lastUpdated": datetime.now().strftime("%d-%m-%Y %H:%M:%S UTC")
        }
        # print(data)

        await self.dumpContests(data)


if __name__ == "__main__":
    c = Contests()
    asyncio.run(c.getAllContests())
