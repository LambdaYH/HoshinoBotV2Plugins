import random
import string
from time import time
from hashlib import md5
from urllib.parse import quote_plus
from nonebot import CommandSession
from nonebot import NLPSession, IntentCommand
from aiocache import cached
from hoshino import Service, priv, aiorequests
from hoshino.typing import CQEvent

sv = Service('weather',
             manage_priv=priv.ADMIN,
             enable_on_default=True,
             visible=False)

# 防误触
keywords = ('天气帮助', '天气预报帮助', '帮助天气', '搜天气帮助', '查天气帮助', '搜天气', '查天气',
            'weather', '实时天气', '实况天气', '当前天气', '今日天气', '天气简报', '天气预报', '/天气')


APP_ID = '' # 腾讯分词
APP_KEY = '' # 腾讯分词
API_URL = 'https://api.ai.qq.com/fcgi-bin/nlp/nlp_wordpos'


@cached(ttl=10 * 60)
async def get_weather_of_city(city: str) -> str:
    try:
        url = 'http://wthrcdn.etouch.cn/weather_mini?city=' + city
        data_json = await aiorequests.get(url, timeout=10)
        data_json = await data_json.json()
        if 'desc' in data_json:
            if data_json['desc'] == "invilad-citykey":
                return "暂不支持这个城市的数据哦(　^ω^)"
            elif data_json['desc'] == "OK":
                city_real = data_json['data']['city']
                w_type = data_json['data']['forecast'][0]['type']
                w_max = data_json['data']['forecast'][0]['high'][3:]
                w_min = data_json['data']['forecast'][0]['low'][3:]
                fengli = data_json['data']['forecast'][0]['fengli'][9:-3]
                ganmao = data_json["data"]["ganmao"]

                repass = f'{city_real}的天气是' + w_type + "天\n最高温度:" + w_max + "\n最低温度:" + w_min + "\n风力:" + fengli + "\n" + ganmao

                return repass
    except:
        return "天气查询失败了~"


@sv.on_command('weather_NLP')
async def weather_NLP(session: CommandSession):
    if not str(session.event.raw_message).startswith(keywords):
        city = session.get('city',
                           prompt=random.choice([
                               '是哪个城市的天气呢？', '请告诉我您需要查哪个城市的天气哦~',
                               '需要查天气吗？哪个城市呢'
                           ]))
        msg = await get_weather_of_city(city)
        if msg:
            await session.send(msg, at_sender=True)
    else:
        pass


@sv.on_natural_language(keywords={'天气'}, only_to_me=False)
async def _(session: NLPSession):
    stripped_msg = session.msg_text.strip()
    params = {
        'app_id': APP_ID,
        'text': stripped_msg.encode('GBK'),
        'time_stamp': str(int(time())),
        'nonce_str': await rand_string(),
    }
    sign = await getReqSign(params)
    params['sign'] = sign
    city = None
    try:
        resp = await aiorequests.post(API_URL, params=params, timeout=10)
        resp = await resp.json()
        for word in resp['data']['mix_tokens']:
            if word['pos_code'] == 20:
                city = word['word']
                break
    except:
        pass
    return IntentCommand(90.0, 'weather_NLP', current_arg=city or '')


@weather_NLP.args_parser
async def _(session: CommandSession):
    stripped_arg = session.current_arg_text.strip()
    if session.is_first_run:
        if stripped_arg:
            session.state['city'] = stripped_arg
        return
    if not stripped_arg:
        session.pause('抱歉，没收到城市信息呢')
    session.state[session.current_key] = stripped_arg


async def getReqSign(params: dict) -> str:
    hashed_str = ''
    for key in sorted(params):
        hashed_str += key + '=' + quote_plus(params[key]) + '&'
    hashed_str += 'app_key=' + APP_KEY
    sign = md5(hashed_str.encode())
    return sign.hexdigest().upper()


async def rand_string(n=8):
    return ''.join(
        random.choice(string.ascii_uppercase + string.digits)
        for _ in range(n))
