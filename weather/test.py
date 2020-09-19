import sqlite3
import os

conn = sqlite3.connect(r'ff14weather.db')
cursor = conn.cursor()
# 执行语句


def getWeatherID(rateID):
    sql = f"select rate from weatherRate where rateID='{rateID}'"
    try:
        results = cursor.execute(sql)
        rateList = results.fetchall()
        print(rateList)
        if rateList==[]:
            raise NameError        
        for item in rateList:
            weather_rate = item[0]
            print(weather_rate)
    except NameError:
        return -1



if __name__ == "__main__":
    getWeatherID(8)


    
# 遍历打印输出