import httpx
import asyncio

from typing import List
from bs4 import BeautifulSoup
from datetime import datetime, timezone


def timeToSeconds(duration):
    parts = duration.split()
    units = {
        "days": 24 * 60 * 60,
        "hours": 60 * 60,
        "minutes": 60,
        "seconds": 1,
        "day": 24 * 60 * 60,
        "hour": 60 * 60,
        "minute": 60,
        "second": 1,
    }

    # When I wrote this, God & I only knew what it did.
    # Now, only God knows what it does. :P
    total = sum(int(parts[i - 1]) * units[parts[i]] for i in range(1, len(parts), 2))

    return total


class Pending:
    urls = []


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
    """
    soup = BeautifulSoup(r.content, "lxml")
    contests = soup.find("div", class_="col-md-9")
    data = []
    # with open("toph.html", "w") as f:
    #     f.write(str(contests.prettify()))

    contests = contests.findAll("tr")

    for i in contests:
        timeData = i.find("span", class_="timestamp")
        if not timeData:
            continue

        x = i.find("a")
        name = x.text
        url = x["href"]
        timestamp = timeData["data-timestamp"]
        startTime = datetime.strftime(
            datetime.fromtimestamp(int(timestamp), timezone.utc), "%Y-%m-%dT%H:%M:%SZ"
        )
        if datetime.now(timezone.utc) > datetime.fromtimestamp(
            int(timestamp), timezone.utc
        ):
            continue

        contest_list = [name, url[3:], startTime]
        data.append(contest_list)

        # To get the duration of the contest
        Pending.urls.append("https://toph.co" + url)

    return data


def extractDuration(r: httpx.Response) -> int:
    """
    Extracts the duration of a contest from a Toph webpage.

    Args:
        r (httpx.Response): The HTTP response object containing the HTML content of the Toph contest webpage.

    Returns:
        int: The duration of the contest in seconds.
    """
    soup = BeautifulSoup(r.content, "lxml")

    with open("toph.html", "w") as f:
        f.write(str(soup.prettify()))
    
    span = (
        soup.findAll("span", {"data-timestamp-type": "proper"})[-1]
        .parent.findAll("strong")[-1]
        .text
    )
    return timeToSeconds(span)


async def getContests(ses: httpx.AsyncClient):
    r = await ses.get("https://toph.co/contests/all")
    loop = asyncio.get_event_loop()
    data = await loop.run_in_executor(None, extractData, r)

    tasks = await asyncio.gather(*[ses.get(i) for i in Pending.urls])
    for i, r in enumerate(tasks):
        try:
            duration = extractDuration(r)
            data[i].append(duration)
        except Exception as e:
            data[i].append(-1)
            print(f"Error in Toph: {i} - {e}")

    return data


if __name__ == "__main__":
    from pprint import pprint

    pprint(asyncio.run(getContests(httpx.AsyncClient(timeout=None))))
