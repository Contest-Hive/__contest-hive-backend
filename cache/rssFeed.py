import datetime
import json

with open("Data/all.json", "rb") as f:
    allJson = json.load(f)


pascalNames = {
    "atcoder": "AtCoder",
    "codechef": "CodeChef",
    "codeforces": "CodeForces",
    "codeforces_gym": "CodeForces Gym",
    "hackerearth": "HackerEarth",
    "hackerrank": "HackerRank",
    "leetcode": "LeetCode",
    "toph": "Toph",
}

urlData = {
    "atcoder": "https://atcoder.jp/contests/",
    "codechef": "https://www.codechef.com/",
    "codeforces": "https://codeforces.com/contests/",
    "codeforces gym": "https://codeforces.com/gymRegistration/",
    "hackerearth": "https://",
    "hackerrank": "https://www.hackerrank.com/contests/",
    "leetcode": "https://leetcode.com/contest/",
    "toph": "https://toph.co/c/",
}

contests = []


for platform, data in allJson["data"].items():
    platform = pascalNames[platform]
    for item in data:
        title, url, startTime, duration = item
        url = urlData[platform.lower()] + url
        contests.append(
            {
                "title": title,
                "url": url,
                "startTime": startTime,
                "duration": duration,
                "platform": platform,
            }
        )


contests.sort(key=lambda x: x["startTime"])

# convert start time to this format Sat, 07 Sep 2002 09:42:31 GMT
for i in range(len(contests)):
    contests[i]["startTime"] = datetime.datetime.strptime(
        contests[i]["startTime"], "%Y-%m-%dT%H:%M:%S%z"
    ).strftime("%a, %d %b %Y %H:%M:%S GMT")


rssTemplate = """\
<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>Contest Hive RSS Feed</title>
    <link>http://contest-hive.vercel.app</link>
    <description>Stay updated with the latest coding contests.</description>
    <language>en-us</language>
    <lastBuildDate>{buildTime}</lastBuildDate>
    {items}
  </channel>
</rss>
"""

currentTime = datetime.datetime.now().strftime("%a, %d %b %Y %H:%M:%S GMT")


def secondsToTime(s):
    s = int(s)
    m, s = divmod(s, 60)
    h, m = divmod(m, 60)
    d, h = divmod(h, 24)
    d = int(d)
    h = int(h)
    m = int(m)
    result = ""
    if d > 0:
        result += f"{d} day{'s' if d > 1 else ''}"
    if h > 0:
        result += f" {h} hour{'s' if h > 1 else ''}"
    if m > 0:
        result += f" {m} minute{'s' if m > 1 else ''}"

    if s:
        result += f" {s} second{'s' if s > 1 else ''}"
    return result.strip()


allItems = []

for i in contests:
    itemTemplate = """
<item>
    <title>{title}</title>
    <link>{url}</link>
    <description>
<![CDATA[
Contest in {platform}
<br/><br/>
Starting in: {relativeStartTime}
<br/><br/>
Contest Name: {title}
<br/>
Link: <a href="{url}">{url}</a>
<br/>
Platform: {platform}
<br/>
Start Time: {startTime}
<br/>
Duration: {duration}    
<br/>
]]>
    </description>
    <guid>{url}</guid>
    <category>Contest</category>  
    <pubDate>{startTime}</pubDate>
</item>
    """
    i["duration"] = secondsToTime(i["duration"])
    i["title"] = i["title"].replace("&", "&amp;")
    i["url"] = i["url"].replace("&", "&amp;")
    i["platform"] = i["platform"].replace("&", "&amp;")
    timeLeft = datetime.datetime.strptime(
        i["startTime"], "%a, %d %b %Y %H:%M:%S GMT") - datetime.datetime.now()
    i["relativeStartTime"] = secondsToTime(timeLeft.total_seconds())

    itemTemplate = itemTemplate.format(**i)
    allItems.append(itemTemplate)

rssTemplate = rssTemplate.format(
    buildTime=currentTime, items="\n".join(allItems))

with open("Data/rss.xml", "w", encoding="utf-8") as f:
    f.write(rssTemplate.strip())
