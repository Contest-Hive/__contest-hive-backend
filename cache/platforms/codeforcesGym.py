import httpx
import asyncio

from typing import List
from datetime import datetime
from bs4 import BeautifulSoup


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
    contests = soup.find("div", class_="datatable").find_all("tr")[1:]

    for contest in contests:
        contest_id = contest.get("data-contestid")
        contest_data = contest.find_all("td")
        status = contest_data[3].text.strip().lower()
        if not status.startswith("before"):
            break  # the contests are sorted by time, so we can break here

        name = contest_data[0].text.strip()
        anchor = contest_data[0].find("a")
        # The name contains weird things sometimes, <a> tag!
        for i in ("\r\n", "\n", "\r", "\t"):
            name = name.replace(i, "")
        if anchor:
            name = name.replace(anchor.text.strip(), "")

        name = name.replace("   ", " ").replace("  ", " ").strip()

        url = contest_id

        startTime = datetime.strptime(
            contest_data[1].text.strip(), "%b/%d/%Y %H:%M"
        ).strftime("%Y-%m-%dT%H:%M:%SZ")
        duration = contest_data[2].text.strip()
        hh, mm = duration.split(":")
        durationSec = int(hh) * 3600 + int(mm) * 60

        contest_list = [name, url, startTime, durationSec]
        data.append(contest_list)

    return data


async def getContestsFromAPI(ses: httpx.AsyncClient):
    url = "https://codeforces.com/api/contest.list?gym=true"
    mirror = "https://mirror.codeforces.com/api/contest.list?gym=true"
    try:
        response = await ses.get(url)
    except Exception as e:
        print("Codeforces GYM API Failed, trying mirror...")
        response = await ses.get(mirror)

    contests = response.json()["result"]
    data = []
    for contest in contests:
        if contest["phase"] == "BEFORE":
            name = contest["name"]
            url = f"https://codeforces.com/contest/{contest['id']}"
            startTime = contest["startTimeSeconds"]
            duration = contest["durationSeconds"]
            data.append([name, url, startTime, duration])

    return data


async def getContests(ses: httpx.AsyncClient):
    url = "https://codeforces.com/gyms?complete=true"
    mirror = "https://mirror.codeforces.com/gyms?complete=true"

    stages = {
        1: ses.get(url),
        2: ses.get(mirror),
        3: getContestsFromAPI(ses),
    }
    count = 1
    while count <= 3:
        try:
            if count == 3:  # API
                print("Using Codeforces GYM API...")
                return await stages[count]

            response = await stages[count]
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, extractData, response)
        except Exception as e:
            print(f"Codeforces GYM {count} Failed, trying next stage...")
            count += 1

    print("Codeforces GYM failed, returning empty list")
    return []


if __name__ == "__main__":
    from pprint import pprint

    pprint(asyncio.run(getContests(httpx.AsyncClient(timeout=None))))
