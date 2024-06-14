# sends message in the telegram channel when a new contest is added

import os
import json
import httpx
import string
import datetime


from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

db = MongoClient(os.environ.get("MONGO_URI"))["Projects"]["contests"]
# db.delete_many({})  # Clear the database
# db.update_one({"_id": 1}, {"$set": {"count": 1}}, upsert=True)
# exit()

channelID = -1002089353416  # @ContestHive
bot_token = os.environ.get("BOT_TOKEN")
messageUrl = f"https://api.telegram.org/bot{bot_token}/sendMessage"
session = httpx.Client(timeout=30, follow_redirects=True)


with open("Data/all.json") as f:
    data = json.load(f)["data"]

urlData = {
    "atcoder": "atcoder.jp/contests/",
    "codechef": "www.codechef.com/",
    "codeforces": "codeforces.com/contests/",
    "codeforces_gym": "codeforces.com/gymRegistration/",
    "hackerearth": "",  # No predefined URL format
    "hackerrank": "www.hackerrank.com/contests/",
    "leetcode": "leetcode.com/contest/",
    "toph": "toph.co/c/",
}


def readableTime(seconds: int) -> str:
    days = seconds // 86400
    seconds %= 86400
    hours = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60

    time = ""
    if days:
        time += f"{days}d "
    if hours:
        time += f"{hours}h "
    if minutes:
        time += f"{minutes}m "
    if seconds:
        time += f"{seconds}s "

    return time.strip()


def cleanText(text: str) -> str:
    printable = string.printable
    return "".join(filter(lambda x: x in printable, text))


for platform, contests in data.items():
    for contest in contests:
        """
        - Type of

        contest = ["AtCoder Beginner Contest 356", "abc356", "2024-06-01T12:00:00Z", 6000]
                    title, urlSuffix, startTime, duration
        """

        title, urlSuffix, startTime, duration = contest
        url = urlData[platform] + urlSuffix

        if url.endswith("/"):
            url = url[:-1]

        if db.find_one({"_id": url}) or duration <= 0:  # using the url as the id
            continue

        contestCount = db.find_one({"_id": 1})["count"]
        title = cleanText(title)
        duration = readableTime(duration)
        utcStartTime = startTime
        then = datetime.datetime.strptime(startTime, "%Y-%m-%dT%H:%M:%SZ").replace(
            tzinfo=datetime.timezone.utc
        )
        now = datetime.datetime.now(datetime.UTC)
        if now > then:
            continue

        startTime = datetime.datetime.strptime(startTime, "%Y-%m-%dT%H:%M:%SZ")
        localTimeUrl = f"https://www.timeanddate.com/worldclock/fixedtime.html?iso={then.strftime('%Y%m%dT%H%M')}"
        print(localTimeUrl)

        startTime = startTime.strftime("%d %B %Y, %I:%M %p")

        message = f"""
🎉 <b>Contest <i>{contestCount}</i></b> at #<b>{platform.capitalize()}</b>
<a href="https://{url}"> </a>
📮 <b>{title}</b>
⏱ <b>{startTime} <a href="{localTimeUrl}"><i>UTC</i></a></b>
⏳ <b>{duration}</b>
🔗 <b><a href="https://{url}">Register now</a></b>

Sent by <a href="https://contest-hive.vercel.app/">Contest Hive</a>
"""

        # Define the payload
        payload = {
            "chat_id": channelID,
            "text": message,
            "parse_mode": "HTML",
            # "disable_notification": True,
            # "disable_web_page_preview": platform.lower() == "codechef",
            # "reply_markup": '{"inline_keyboard": [[{"text": "Go to Contest", "url": "😀"}]]}'.replace(
            #     "😀", f"https://{url}"
            # ),
        }

        # Send the POST request
        response = session.post(messageUrl, data=payload)

        db.insert_one(
            {
                "_id": url,
                "title": title,
                "platform": platform,
                "startTime": utcStartTime,
                "duration": duration,
                "addedAt": datetime.datetime.now(datetime.UTC),
            }
        )
        db.update_one({"_id": 1}, {"$inc": {"count": 1}})

        print(f"Added {title} from {platform} to the database.")
