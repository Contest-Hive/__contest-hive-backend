# Contest Hive ( BackEnd )

## Description

This is the backend of the [Contest Hive](https://contest-hive.vercel.app) project.

Visit the repository at: https://github.com/Nusab19/Contest-Hive

It uses Github Actions to run a python script that scrapes contest information from the following platforms:

- [AtCoder](https://atcoder.jp/)
- [CodeChef](https://www.codechef.com/)
- [Codeforces](https://codeforces.com/)
- [HackerEarth](https://www.hackerearth.com/)
- [HackerRank](https://www.hackerrank.com/)
- [LeetCode](https://leetcode.com/)
- [Toph](https://toph.co/)

This runs every 11 minutes and pushes the data to itself. The data is then accessed by the frontend.

## Warning

The python script should not be misused. It is intended to be used by the backend only. Do not try to DDoS the platforms by running the script too often.

## Author

- [Nusab Taha](https://nusab19.pages.dev/)
