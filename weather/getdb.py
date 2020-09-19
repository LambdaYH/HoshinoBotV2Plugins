# -*- coding:utf-8 -*-
import json
import sqlite3

DB_FILE = "ff14weather.db"
conn = sqlite3.connect(DB_FILE)
c = conn.cursor()
try:
    c.execute("drop table territory")
except:
    pass
finally:
    c.execute('create table territory (name Text , nickname Text , weather_rate Text , mapid Text)')

try:
    c.execute("drop table weather")
except:
    pass
finally:   
    c.execute('create table weather (name Text, weatherID Text)')

try:
    c.execute("drop table weatherRate")
except:
    pass
finally:
    c.execute('create table weatherRate (rate Text, rateID Text)')
print("create table success")
conn.commit()
territoryList = json.load(open("Territory.json",encoding='utf-8'))
weatherList = json.load(open("Weather.json",encoding='utf-8'))
weatherRateList = json.load(open("weatherRate.json",encoding='utf-8'))
for item in territoryList:
    name = item['fields']['name']
    nickname = item['fields']['nickname']
    weather_rate = item['fields']['weather_rate']
    mapid = item['fields']['mapid']
    data = [name,nickname,weather_rate,mapid]
    c.execute('insert into territory values (?,?,?,?)', data)
    conn.commit()
for item in weatherList:
    name = item['fields']['name']
    weatherID = item['pk']
    data = [name,weatherID]
    c.execute('insert into weather values (?,?)', data)
    conn.commit()
    
for item in weatherRateList:
    rate = item['fields']['rate']
    rateID = item['pk']
    data = [rate,rateID]
    c.execute('insert into weatherRate values (?,?)', data)
    conn.commit()

    print('insert into territory values ' + str(data) +" success")

c.close()