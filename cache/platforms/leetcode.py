import os
import json
import httpx
import asyncio

from typing import List
from datetime import datetime
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# load_dotenv()


def extractData(r: httpx.Response) -> List[List[str]]:
    """
    Extracts contest data from a LeetCode webpage and returns it as a list of lists.

    Args:
        r (httpx.Response): The HTTP response object containing the HTML content of the LeetCode contests webpage.

    Returns:
        List[List[str]]: A list of lists representing the contest data. Each inner list contains the following information:
            - Name of the contest
            - URL of the contest
            - Start time of the contest in ISO 8601 format
            - Duration of the contest in seconds
    """
    data = []
    soup = BeautifulSoup(r.content, "lxml")
    a = json.loads(soup.find("script", id="__NEXT_DATA__").text)
    contests = a["props"]["pageProps"]["dehydratedState"]["queries"][-1]["state"][
        "data"
    ]["topTwoContests"]

    for i in contests:
        name = i["title"]
        url = i["titleSlug"]
        startSec = i["startTime"]
        startTime = datetime.strftime(
            datetime.utcfromtimestamp(startSec), "%Y-%m-%dT%H:%M:%SZ"
        )

        durationSec = i["duration"]
        contest_list = [name, url, startTime, durationSec]
        data.append(contest_list)

    return data


async def getContests(ses: httpx.AsyncClient):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
    }
    proxy = os.environ.get("PROXY")

    if proxy:
        proxies = {"http://": proxy, "https://": proxy}
        ses = httpx.AsyncClient(proxies=proxies, timeout=33, follow_redirects=True)
    else:
        print("No proxy found")

    response = await ses.get("https://leetcode.com/contest/", headers=headers)
    if response.status_code != 200:
        print(f"Failed to fetch LeetCode contests: {response.status_code}")
        return []
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, extractData, response)


if __name__ == "__main__":
    from pprint import pprint

    pprint(asyncio.run(getContests(httpx.AsyncClient(timeout=None))))
