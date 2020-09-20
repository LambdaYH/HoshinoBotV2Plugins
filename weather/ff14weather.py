import json
import traceback
import time
import sqlite3

TIMEFORMAT_MDHMS = f"%m-%d %H:%M:%S"
TIMEFORMAT= f"%Y-%m-%d %H:%M:%S"

DB_PATH = "/root/HoshinoBot/hoshino/modules/weather/ff14weather.db"


async def getEorzeaHour(unixSeconds):
    bell = (unixSeconds / 175) % 24
    return int(bell)

async def calculateForecastTarget(unixSeconds):
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

async def getWeatherTimeFloor(unixSeconds):
    # Get Eorzea hour for weather start
    bell = (unixSeconds / 175) % 24
    startBell = bell - (bell % 8)
    startUnixSeconds = round(unixSeconds - (175 * (bell - startBell)))
    return startUnixSeconds


async def getWeatherID(chance, rateID):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    sql = f"select rate from weatherRate where rateID='{rateID}'"
    try:
        results = cursor.execute(sql)
        rateList = results.fetchall()
        if rateList!=[]:
            for item in rateList:
                weather_rate = item[0]
        else:
            raise NameError  
    except NameError:
        return -1
    lrate = 0
    for (weather_id, rate) in json.loads(weather_rate):
        if lrate <= chance < lrate + rate:
            return weather_id
        lrate += rate
    return -1


async def getFollowingWeathers(rateID, cnt=5, TIMEFORMAT="%m-%d %H:%M:%S", **kwargs):
    unixSeconds = kwargs.get("unixSeconds", int(time.time()))
    weatherStartTime = await getWeatherTimeFloor(unixSeconds)
    now_time = weatherStartTime
    weathers = []
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    for i in range(cnt):
        chance = await calculateForecastTarget(now_time)
        weather_id = await getWeatherID(chance,rateID)
        pre_chance = await calculateForecastTarget(now_time - 8 * 175)
        pre_weather_id = await getWeatherID(pre_chance, rateID)
        # print("weather_id:{}".format(weather_id))
        try:
            sql = f"select name from weather where weatherID='{weather_id}'"
            results = cursor.execute(sql)
            weatherList = results.fetchall()
            print(weatherList)
            if weatherList!=[]:
                for item in weatherList:
                    weather = item[0]
            else:
                weather = None
                raise NameError
        except NameError:
            raise

        try:
            sql = f"select name from weather where weatherID='{pre_weather_id}'"
            results = cursor.execute(sql)
            weatherList = results.fetchall()
            if weatherList!=[]:
                for item in weatherList:
                    pre_weather = item[0]
            else:
                pre_weather=None
                raise NameError
        except NameError:
            raise
        weathers.append(
            {
                "pre_name": f"{pre_weather}",
                "name": f"{weather}",
                "ET": f"{await getEorzeaHour(now_time)}:00",
                "LT": f"{time.strftime(TIMEFORMAT, time.localtime(now_time))}",
            }
        )
        now_time += 8 * 175
    return weathers

async def get_ff14weather(territory_name):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
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
        raise
    weathers = await getFollowingWeathers(
        rateID, 5, TIMEFORMAT_MDHMS, unixSeconds = time.time()
    )
    msg = f"接下来{territory}的天气预报如下："
    for item in weathers:
        msg += "\n{} ET:{}\tLT:{}".format(
            "{}->{}".format(item["pre_name"], item["name"]),
            item["ET"],
            item["LT"],
        )
    return msg
