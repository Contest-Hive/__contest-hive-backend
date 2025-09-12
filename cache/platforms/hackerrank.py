import httpx
import asyncio

from datetime import datetime
from typing import List


def extractData(r: httpx.Response) -> List[List[str]]:
    """
    Extracts contest data from a HackerRank webpage and returns it as a list of lists.

    Args:
        r (httpx.Response): The HTTP response object containing the HTML content of the HackerRank contests webpage.

    Returns:
        List[List[str]]: A list of lists representing the contest data. Each inner list contains the following information:
            - Name of the contest
            - URL of the contest
            - Start time of the contest in ISO 8601 format
            - Duration of the contest in seconds
    """
    data = []
    contests = r.json()["models"]
    for i in contests:
        started = i["started"]
        ended = i["ended"]
        if started or ended:
            continue
        name = i["name"]
        url = i["slug"]
        startTime = datetime.strptime(i["get_starttimeiso"], "%Y-%m-%dT%H:%M:%SZ")
        endTime = datetime.strptime(i["get_endtimeiso"], "%Y-%m-%dT%H:%M:%SZ")
        durationSec = int((endTime - startTime).total_seconds())
        startTime = startTime.strftime("%Y-%m-%dT%H:%M:%SZ")
        contest_list = [name, url, startTime, durationSec]
        data.append(contest_list)

    return data


async def getContests(ses: httpx.AsyncClient):
    headers = {
        "User-Agent": "Mozilla/5.0 (iPad; U; CPU OS 3_2_1 like Mac OS X; en-us) AppleWebKit/531.21.10 (KHTML, like Gecko) Mobile/7B405"
    }

    response = await ses.get(
        "https://www.hackerrank.com/rest/contests/upcoming", headers=headers
    )
    loop = asyncio.get_event_loop()

    return await loop.run_in_executor(None, extractData, response)


if __name__ == "__main__":
    from pprint import pprint

    pprint(asyncio.run(getContests(httpx.AsyncClient(timeout=None))))
