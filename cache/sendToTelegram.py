# send message in the telegram channel when a new contest is added

import os
import json
import datetime

from dotenv import load_dotenv
from pymongo import MongoClient
from telegram import Bot, constants, InlineKeyboardButton, InlineKeyboardMarkup

load_dotenv()

db = MongoClient(os.environ.get("MONGO_URI"))["Projects"]["contests"]
bot = Bot(token=os.environ.get("BOT_TOKEN"))
channelID = -1002089353416  # @ContestHive

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

        if db.find_one({"_id": url}):  # using the url as the id
            continue

        db.insert_one(
            {
                "_id": url,
                "title": title,
                "platform": platform,
                "startTime": startTime,
                "duration": duration,
                "addedAt": datetime.datetime.now(datetime.UTC),
            }
        )

        startTime = datetime.datetime.strptime(
            startTime, "%Y-%m-%dT%H:%M:%SZ"
        ).strftime("%d %B %Y, %I:%M %p")

        message = f"""
🏆 <b>{platform.capitalize()}</b>

📅 <b>{title}</b>
🕒 <b>Start Time:</b> {startTime}
⏰ <b>Duration:</b> {duration // 60} minutes
🔗 [Link]({url})

🤖 [Contest Hive](https://contest-hive.vercel.app/)
"""
        buttons = [[InlineKeyboardButton("Go to Contest", url=f"https://{url}")]]

        bot.sendMessage(
            channelID,
            message,
            parse_mode=constants.ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup(buttons),
            disable_web_page_preview=True,
            disable_notification=True,
            timeout=30,
        )
        print(f"Added {title} from {platform} to the database.")
