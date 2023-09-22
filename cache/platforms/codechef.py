import pytz
import httpx
import asyncio

from datetime import datetime
from typing import List


def extractData(r: httpx.Response) -> List[List[str]]:
    """
    Extracts contest data from a CodeChef webpage and returns it as a list of lists.

    Args:
        r (httpx.Response): The HTTP response object containing the HTML content of the CodeChef contests webpage.

    Returns:
        List[List[str]]: A list of lists representing the contest data. Each inner list contains the following information:
            - Name of the contest
            - URL of the contest
            - Start time of the contest in ISO 8601 format
            - Duration of the contest in seconds
    """
    r = r.json()

    if r.get("status") != "success":
        return []

    data = []
    contests = r["future_contests"]

    for i in contests:
        name = i["contest_name"]
        url = i["contest_code"]
        startIso = i["contest_start_date_iso"]
        startTime = datetime.fromisoformat(startIso).astimezone(
            pytz.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        durationSec = int(i["contest_duration"]) * 60
        contest_list = [name, url, startTime, durationSec]

        data.append(contest_list)

    return data


async def getContests(ses: httpx.AsyncClient):
    response = await ses.get("https://www.codechef.com/api/list/contests/all")
    loop = asyncio.get_event_loop()

    return await loop.run_in_executor(None, extractData, response)

if __name__ == "__main__":
    from pprint import pprint
    pprint(asyncio.run(getContests(httpx.AsyncClient(timeout=None))))
