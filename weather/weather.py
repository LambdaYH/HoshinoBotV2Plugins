from jieba import posseg
from nonebot import CommandSession
from nonebot import NLPSession, IntentCommand
from aiocache import cached
import http.client
import json
import urllib

import requests
from bs4 import BeautifulSoup
from hoshino import Service, priv
from hoshino.typing import CQEvent

sv = Service('weather',
             manage_priv=priv.ADMIN,
             enable_on_default=True,
             visible=False)
             
@cached(ttl=10 * 60)
async def get_weather(city_name):
    city_code = await get_city_code(city_name)
    weather_info, city_name = await get_info(city_code)
    if weather_info and city_name:
        res = city_name + '的天气预报如下：'
        for each in weather_info:
            res += '\n' + each[0] + ' ' + each[1] + ' '
            if each[2]:
                res += each[2] + '/'
            res += each[3]
        return res
    else:
        return '天气查询失败'

@cached(ttl=10 * 60)
async def get_weather_NLP(city_name):
    city_code = await get_city_code(city_name)
    weather_info, city_name = await get_info(city_code)
    if weather_info and city_name:
        res = city_name + '的天气预报如下：'
        for each in weather_info:
            res += '\n' + each[0] + ' ' + each[1] + ' '
            if each[2]:
                res += each[2] + '/'
            res += each[3]
        return res
    else:
        return None


@cached(ttl=10 * 60)
async def get_info(city_code):
    try:
        url = 'http://www.weather.com.cn/weather/' + city_code + '.shtml'
        r = requests.get(url, timeout=15)
        r.encoding = 'utf-8'
        soup = BeautifulSoup(r.text, 'lxml')
        div = soup.find('div', {'id': '7d'})
        li = div.find('ul').find_all('li')
        city_fullname_list = soup.find('div', class_="crumbs fl").text.replace(
            " ", "").replace("\n", "").replace("\r",
                                               "").replace("\t",
                                                           "").split(">")[-2:]
        city_fullname = city_fullname_list[-2] + "-" + city_fullname_list[-1]
        week_info = []
        for each in li:
            day_info = []
            day_info.append(each.find('h1').string)
            p = each.find_all('p')
            day_info.append(p[0].string)
            if p[1].find('span') is None:
                temp_high = None
            else:
                temp_high = p[1].find('span').string
            temp_low = p[1].find('i').string
            day_info.append(temp_high)
            day_info.append(temp_low)
            week_info.append(day_info)
        return week_info, city_fullname
    except:
        return None, None


@cached(ttl=10 * 60)
async def get_city_code(city_name):
    try:
        parameter = urllib.parse.urlencode({'cityname': city_name})
        conn = http.client.HTTPConnection('toy1.weather.com.cn', 80, timeout=5)
        conn.request('GET', '/search?' + parameter)
        r = conn.getresponse()
        data = r.read().decode()[1:-1]
        json_data = json.loads(data)
        code = json_data[0]['ref'].split('~')[0]
        return code
    except:
        return None

@sv.on_prefix(('天气预报', '查天气'))
async def weather(bot, ev: CQEvent):
    city = ev.message.extract_plain_text().strip()
    if city:
        msg = await get_weather(city)
    else:
        msg = "要查询的城市名称不能为空，请重新输入"
    await bot.send(ev, msg, at_sender=True)


@sv.on_command('weather_NLP')
async def weather_NLP(session: CommandSession):
    city = session.get('city')
    msg = await get_weather_NLP(city)
    if msg:
        await session.send(msg, at_sender=True)


@sv.on_natural_language(keywords={'天气'}, only_to_me=False)
async def _(session: NLPSession):
    stripped_msg = session.msg_text.strip()
    words = posseg.lcut(stripped_msg)
    city = None
    for word in words:
        if word.flag == 'ns':
            city = word.word
            break
    return IntentCommand(90.0, 'weather_NLP', current_arg=city or '')

@weather_NLP.args_parser
async def _(session: CommandSession):
    stripped_arg = session.current_arg_text.strip()
    if session.is_first_run:
        if stripped_arg:
            session.state['city'] = stripped_arg
        return
    if not stripped_arg:
        session.pause('要查询的城市名称不能为空，请重新输入')
    session.state[session.current_key] = stripped_arg
