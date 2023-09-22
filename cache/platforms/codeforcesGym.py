import httpx
import asyncio

from datetime import datetime
from bs4 import BeautifulSoup
from typing import List


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
            break

        name = contest_data[0].text.strip()
        url = f"{contest_id}"
        startTime = datetime.strptime(contest_data[1].text.strip(
        ), "%b/%d/%Y %H:%M").strftime("%Y-%m-%dT%H:%M:%SZ")
        duration = contest_data[2].text.strip()
        hh, mm = duration.split(":")
        durationSec = int(hh) * 3600 + int(mm) * 60

        contest_list = [name, url, startTime, durationSec]
        data.append(contest_list)

    return data


async def getContests(ses: httpx.AsyncClient):
    response = await ses.get("https://codeforces.com/gyms")
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, extractData, response)

if __name__ == "__main__":
    from pprint import pprint
    pprint(asyncio.run(getContests(httpx.AsyncClient(timeout=None))))
