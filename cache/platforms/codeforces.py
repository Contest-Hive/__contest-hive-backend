import httpx
import asyncio

from typing import List
from datetime import datetime
from bs4 import BeautifulSoup


def parseDuration(duration: str) -> int:
    duration = duration.split(":")
    duration = list(map(int, duration))
    durationSeconds = 0
    length = len(duration)
    for i in range(length):
        durationSeconds += duration[i] * (60 ** (length - i - 1))

    # 02:00 -> 2 hours, not 2 minutes. That's the reason for multiplying by 60
    return durationSeconds * 60


def extractData(r: httpx.Response) -> List[List[str]]:
    """
    Extracts contest data from a Codeforces webpage and returns it as a list of lists.

    Args:
        r (httpx.Response): The HTTP response object containing the HTML content of the Codeforces contests webpage.

    Returns:
        List[List[str]]: A list of lists representing the contest data. Each inner list contains the following information:
            - Name of the contest
            - URL of the contest
            - Start time of the contest in ISO 8601 format
            - Duration of the contest in seconds
    """
    data = []
    soup = BeautifulSoup(r.content, "lxml")
    print(soup)
    contests = soup.find("div", class_="datatable").find_all("tr")[1:]

    for contest in contests:
        contest_id = contest.get("data-contestid")
        contest_data = contest.find_all("td")
        name = contest_data[0].text.strip()
        anchor = contest_data[0].find("a")

        # The name contains weird things sometimes, <a> tag!
        for i in ("\r\n", "\n", "\r", "\t"):
            name = name.replace(i, "")
        if anchor:
            name = name.replace(anchor.text.strip(), "")

        name = name.replace("   ", " ").replace("  ", " ").strip()

        url = contest_id  # f"https://codeforces.com/contest/{contest_id}"

        # the time format is in Moscow time, so we need to add +0300 to it to convert it to UTC
        startDate = contest_data[2].text.strip() + " +0300"
        startTime = datetime.strptime(startDate, "%b/%d/%Y %H:%M %z").utctimetuple()
        startTime = datetime(*startTime[:6]).isoformat() + "Z"

        duration = contest_data[-3].text.strip()
        durationSec = parseDuration(duration)

        contest_list = [name, url, startTime, durationSec]
        data.append(contest_list)

    return data


async def getContestsFromAPI(ses: httpx.AsyncClient):
    url = "https://codeforces.com/api/contest.list"
    mirror = "https://mirror.codeforces.com/api/contest.list"
    try:
        response = await ses.get(url)
    except Exception as e:
        print("Codeforces API Failed, trying mirror...")
        response = await ses.get(mirror)

    contests = response.json()["result"]
    data = []
    for contest in contests:
        if contest["phase"] == "BEFORE":
            name = contest["name"]
            # url = f"https://codeforces.com/contest/{contest['id']}"
            url = url = contest["id"]
            startTimeStamp = contest["startTimeSeconds"]  # timestamp eg. 1743847200
            startTime = datetime.fromtimestamp(startTimeStamp).isoformat() + "Z"
            duration = contest["durationSeconds"]
            data.append([name, url, startTime, duration])

    return data


async def getContests(ses: httpx.AsyncClient):
    url = "https://codeforces.com/contests?complete=true"
    mirror = "https://mirror.codeforces.com/contests?complete=true"

    stages = {
        1: ses.get(url),
        2: ses.get(mirror),
        3: getContestsFromAPI(ses),
    }
    # TODO: Change later if codeforces removes the cloudflare protection
    count = 3  # Start from the API

    while count <= 3:
        try:
            if count == 3:  # API
                print("Using Codeforces API...")
                return await stages[count]

            response = await stages[count]
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, extractData, response)
        except Exception as e:
            print(f"Codeforces {count} Failed, trying next stage...")
            count += 1

    print("Codeforces failed, returning empty list")
    return []


if __name__ == "__main__":
    from pprint import pprint

    pprint(asyncio.run(getContests(httpx.AsyncClient(timeout=None))))
