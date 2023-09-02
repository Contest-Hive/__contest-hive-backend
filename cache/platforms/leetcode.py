import json
import httpx
import asyncio

from bs4 import BeautifulSoup
from datetime import datetime
try:
    from helpers.format_time import secondsToTime, timeToSeconds, humanReadableTime, calculate_time_difference
except ImportError:
    from .helpers.format_time import secondsToTime, timeToSeconds, humanReadableTime, calculate_time_difference



def convert_start_time(startTime):
    dt = datetime.strptime(startTime, "%d-%m-%Y %H:%M:%S UTC")
    formatted_time = dt.strftime("%Y-%m-%dT%H:%M:%S.000+00:00")
    return formatted_time


def extract_data(r):
    soup = BeautifulSoup(r, "lxml")

    a = soup.find("script", id="__NEXT_DATA__")
    data = json.loads(a.text)[
        "props"]["pageProps"]["dehydratedState"]["queries"][-1]["state"]["data"]["topTwoContests"]

    return data


async def getContests(ses: httpx.AsyncClient):
    r = (await ses.get("https://leetcode.com/contest/"))

    loop = asyncio.get_event_loop()
    data = await loop.run_in_executor(None, extract_data, r.text)

    allContests = []

    for i in data:
        name = i["title"]
        url = "https://leetcode.com/contest/" + i["titleSlug"]

        startSec = i["startTime"]
        startTime = datetime.strftime(
            datetime.utcfromtimestamp(startSec),
            "%d-%m-%Y %H:%M:%S") + " UTC"
        startTime = convert_start_time(startTime)
        durationSec = i["duration"]
        duration = secondsToTime(durationSec)
        contest = {
            "name": name,
            "url": url,
            "startTime": startTime,
            "readableStartTime": humanReadableTime(startTime),
            "startingIn": calculate_time_difference(startTime),
            "duration": duration,
            "durationSeconds": durationSec
        }
        allContests.append(contest)

    return allContests


if __name__ == "__main__":
    print("Only running one file.\n")
    a = asyncio.run(getContests(httpx.AsyncClient(timeout=13)))
    for j in a:
        print(j)
