import httpx
import asyncio

from typing import List
from datetime import datetime, UTC


def extractData(r: httpx.Response) -> List[List[str]]:
    """
    Extracts contest data from a AtCoder webpage and returns it as a list of lists.

    Args:
        r (httpx.Response): The HTTP response object containing the HTML content of the AtCoder contests webpage.

    Returns:
        List[List[str]]: A list of lists representing the contest data. Each inner list contains the following information:
            - Name of the contest
            - URL of the contest
            - Start time of the contest in ISO 8601 format
            - Duration in seconds
    """
    jsonData = r.json()["contests"]
    data = []
    for i in jsonData:
        title = i["title"]
        url = i["url"].split('/')[-1]
        startsAt = i["startsAt"]
        duration = i["duration"] * 60
        d = [title, url, startsAt, duration]
        if datetime.fromisoformat(startsAt) > datetime.now(UTC):
            data.append(d)
    
    return data




async def getContests(ses: httpx.AsyncClient):
    r = await ses.get("https://toph.co/contests.json")
    data = extractData(r)

    return data


if __name__ == "__main__":
    from pprint import pprint

    pprint(asyncio.run(getContests(httpx.AsyncClient(timeout=None))))
