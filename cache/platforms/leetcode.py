import os
import json
import httpx
import asyncio

from typing import List
from datetime import datetime
from bs4 import BeautifulSoup

query = """
{
  upcomingContests {
    title
    startTime
    duration
  }
}
"""


async def getContests(ses: httpx.AsyncClient):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
    }
    res = await ses.post("https://leetcode.com/graphql", json={"query": query})
    data = res.json()
    upcoming_contests = data["data"]["upcomingContests"]

    contest_list = []
    for contest in upcoming_contests:
        title = contest["title"]
        url = title.lower().replace(' ', '-')
        start_time = contest["startTime"]
        start_time = datetime.utcfromtimestamp(start_time).strftime("%Y-%m-%dT%H:%M:%SZ")
        duration = contest["duration"]
        contest_list.append([title, url, start_time, duration])
    
    return contest_list

if __name__ == "__main__":
    from pprint import pprint

    pprint(asyncio.run(getContests(httpx.AsyncClient(timeout=None))))
