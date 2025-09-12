from datetime import datetime, timezone


def secondsToTime(s):
    m, s = divmod(s, 60)
    h, m = divmod(m, 60)
    d, h = divmod(h, 24)
    m = int(m)
    h = int(h)
    d = int(d)

    result = ""
    if d > 0:
        result += f"{d} day{'s' if d > 1 else ''}"
    if h > 0:
        result += f" {h} hour{'s' if h > 1 else ''}"
    if m > 0:
        result += f" {m} minute{'s' if m > 1 else ''}"
    if not result:
        result = f"{int(s)} second{'s' if s > 1 else ''}"
    return result.strip()


def timeToSeconds(duration):
    parts = duration.split()
    units = {
        "days": 24 * 60 * 60,
        "hours": 60 * 60,
        "minutes": 60,
        "day": 24 * 60 * 60,
        "hour": 60 * 60,
        "minute": 60,
    }

    total = sum(int(parts[i - 1]) * units[parts[i]] for i in range(1, len(parts), 2))

    return total


def humanReadableTime(startTime: str):
    dt = datetime.fromisoformat(startTime)
    a = dt.strftime("%d %B, %Y %I:%M:%S %p")
    if a.startswith("0"):
        a = a[1:]

    fate = {"1": "st", "2": "nd", "3": "rd"}

    date = a.split()[0]
    finalTime = f"{date}{fate.get(date[-1], 'th')} {a[len(date)+1:]} UTC"

    return finalTime


def calculate_time_difference(time_str):
    dt = datetime.fromisoformat(time_str)
    current_time = datetime.now(timezone.utc)
    time_difference = (dt - current_time).total_seconds()
    return " ".join(secondsToTime(time_difference).split()[:2])
