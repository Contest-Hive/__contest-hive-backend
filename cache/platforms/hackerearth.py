import httpx
import asyncio
from datetime import datetime
from typing import List


def extractData(r: httpx.Response) -> List[List[str]]:
    """
    Extracts contest data from a HackerEarth webpage and returns it as a list of lists.

    Args:
        r (httpx.Response): The HTTP response object containing the HTML content of the HackerEarth contests webpage.

    Returns:
        List[List[str]]: A list of lists representing the contest data. Each inner list contains the following information:
            - Name of the contest
            - URL of the contest
            - Start time of the contest in ISO 8601 format
            - Duration of the contest in seconds
    """

    data = []

    if r.status_code != 200:
        return []

    jr = r.json()
    contests = jr.get("response")
    for i in contests:
        status = i["status"]
        if status != "UPCOMING":
            continue
        name = i["title"]
        url = i["url"]
        startTime = datetime.strptime(i["start_utc_tz"], "%Y-%m-%d %H:%M:%S%z")
        endTime = datetime.strptime(i["end_utc_tz"], "%Y-%m-%d %H:%M:%S%z")
        durationSec = int((endTime - startTime).total_seconds())
        startTime = startTime.strftime("%Y-%m-%dT%H:%M:%SZ")
        url = url[8:]
        if url[-1] == "/":
            url = url[:-1]

        contest_list = [name, url, startTime, durationSec]
        data.append(contest_list)

    return data


async def getContests(ses: httpx.AsyncClient):
    response = await ses.get("https://www.hackerearth.com/chrome-extension/events/")
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, extractData, response)


if __name__ == "__main__":
    from pprint import pprint

    pprint(asyncio.run(getContests(httpx.AsyncClient(timeout=13))))
