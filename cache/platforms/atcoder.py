import pytz
import httpx
import asyncio

from datetime import datetime
from bs4 import BeautifulSoup
from typing import List


def extractData(r: httpx.Response) -> List[List[str]]:
    """
    Extracts contest data from a AtCoder and returns it as a list of lists.

    Args:
        r (httpx.Response): The HTTP response object containing the HTML content of the At contests webpage.

    Returns:
        List[List[str]]: A list of lists representing the contest data. Each inner list contains the following information:
            - Name of the contest
            - URL of the contest
            - Start time of the contest in ISO 8601 format
            - Duration of the contest in seconds
    """
    data = []
    soup = BeautifulSoup(r.content, "lxml")
    contests = soup.select("#contest-table-upcoming tbody tr")

    for con in contests:
        ele = con.find_all("td")
        text = ele[1].text.strip()
        name = text[text.find("\n") + 1:].strip().split()[1:]
        name = " ".join(name)
        url = ele[1].select("a")[0].get("href")[10:]
        text = ele[0].text.strip()
        print(name, text)
        startTime = datetime.strptime(text, "%Y-%m-%d %H:%M:%S%z").astimezone(pytz.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        h, m = ele[2].text.split(':')
        durationSec = int(h) * 3600 + int(m) * 60
        contest_list = [name, url, startTime, durationSec]
        data.append(contest_list)

    return data


async def getContests(ses: httpx.AsyncClient):
    response = await ses.get("https://atcoder.jp/contests/")
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, extractData, response)

if __name__ == "__main__":
    from pprint import pprint
    pprint(asyncio.run(getContests(httpx.AsyncClient(timeout=None))))
