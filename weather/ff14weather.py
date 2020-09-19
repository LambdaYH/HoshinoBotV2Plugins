import logging
import json
import random
import traceback
import time
import sqlite3
import re
import urllib

conn = sqlite3.connect(r'ff14weather.db')
cursor = conn.cursor()

TIMEFORMAT_MDHMS = f"%m-%d %H:%M:%S"
TIMEFORMAT= f"%Y-%m-%d %H:%M:%S"

def getEorzeaHour(unixSeconds):
    bell = (unixSeconds / 175) % 24
    return int(bell)

def calculateForecastTarget(unixSeconds):
    # Thanks to Rogueadyn's SaintCoinach library for this calculation.
    # lDate is the current local time.
    # Get Eorzea hour for weather start
    bell = unixSeconds / 175

    # Do the magic 'cause for calculations 16:00 is 0, 00:00 is 8 and 08:00 is 16
    increment = int(bell + 8 - (bell % 8)) % 24

    # Take Eorzea days since unix epoch
    totalDays = unixSeconds // 4200
    # totalDays = (totalDays << 32) >>> 0; # Convert to uint

    calcBase = totalDays * 100 + increment

    step1 = ((calcBase << 11) % (0x100000000)) ^ calcBase
    step2 = ((step1 >> 8) % (0x100000000)) ^ step1

    return step2 % 100

def getWeatherTimeFloor(unixSeconds):
    # Get Eorzea hour for weather start
    bell = (unixSeconds / 175) % 24
    startBell = bell - (bell % 8)
    startUnixSeconds = round(unixSeconds - (175 * (bell - startBell)))
    return startUnixSeconds


def getWeatherID(chance, rateID):
    sql = f"select rate from weatherRate where rateID='{rateID}'"
    try:
        results = cursor.execute(sql)
        rateList = results.fetchall()
        if rateList==[]:
            raise NameError        
        for item in rateList:
            weather_rate = item[0]
    except NameError:
        return -1
    lrate = 0
    for (weather_id, rate) in json.loads(weather_rate):
        if lrate <= chance < lrate + rate:
            return weather_id
    return -1


def getFollowingWeathers(rateID, cnt=5, TIMEFORMAT="%m-%d %H:%M:%S", **kwargs):
    unixSeconds = kwargs.get("unixSeconds", int(time.time()))
    weatherStartTime = getWeatherTimeFloor(unixSeconds)
    now_time = weatherStartTime
    weathers = []
    for i in range(cnt):
        chance = calculateForecastTarget(now_time)
        weather_id = getWeatherID(chance,rateID)
        pre_chance = calculateForecastTarget(now_time - 8 * 175)
        pre_weather_id = getWeatherID(pre_chance, rateID)
        # print("weather_id:{}".format(weather_id))
        try:
            sql = f"select name from weather where weatherID='{weather_id}'"
            results = cursor.execute(sql)
            weatherList = results.fetchall()
            for item in weatherList:
                weather = item[0]
        except NameError:
            pass

        try:
            sql = f"select name from weather where weatherID='{pre_weather_id}'"
            results = cursor.execute(sql)
            weatherList = results.fetchall()
            for item in weatherList:
                pre_weather = item[0]
        except NameError:
            raise NameError

        weathers.append(
            {
                "pre_name": f"{pre_weather}",
                "name": f"{weather}",
                "ET": f"{getEorzeaHour(now_time)}:00",
                "LT": f"{time.strftime(TIMEFORMAT, time.localtime(now_time))}",
            }
        )
        now_time += 8 * 175
    return weathers

def get_ff14weather(territory_name):
    sql = f"select name, nickname, weather_rate, mapid from territory where name='{territory_name}' or nickname='{territory_name}'"
    try:
        results = cursor.execute(sql)
        territoryList = results.fetchall()
        if territoryList==[]:
            raise NameError
        for item in territoryList:
            territory = item[0]
            rateID = item[2]
    except NameError:
        msg = "找不到所查询区域：{}".format(territory)
    weathers = getFollowingWeathers(
        rateID, 5, TIMEFORMAT_MDHMS, unixSeconds = time.time()
    )
    msg = f"接下来{territory}的天气情况如下："
    for item in weathers:
        msg += "\n{} ET:{}\tLT:{}".format(
            "{}->{}".format(item["pre_name"], item["name"]),
            item["ET"],
            item["LT"],
        )

    return msg

if __name__ == "__main__":
    print(get_ff14weather("格里达尼亚旧街"))