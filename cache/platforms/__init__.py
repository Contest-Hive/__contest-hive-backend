from .atcoder import getContests as AtCoder
from .codechef import getContests as CodeChef
from .codeforces import getContests as CodeForces
from .hackerearth import getContests as HackerEarth
from .hackerrank import getContests as HackerRank
from .leetcode import getContests as LeetCode
from .toph import getContests as Toph

from datetime import datetime

def convert_start_time(startTime):
    dt = datetime.strptime(startTime, "%d-%m-%Y %H:%M:%S UTC")
    formatted_time = dt.strftime("%Y-%m-%dT%H:%M:%S.000+00:00")
    return formatted_time
