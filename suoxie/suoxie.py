import requests
import json
from hoshino.typing import CQEvent, MessageSegment
from hoshino import Service, priv

headers = {
    "content-type":
    "application/json; charset=utf-8",
    "User-Agent":
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36 Edg/85.0.564.41"
}

url = "https://lab.magiconch.com/api/nbnhhsh/guess/"

sv_help = '''
使用方法：
缩写 要查询的缩写
'''

sv = Service('suoxie',
             manage_priv=priv.SUPERUSER,
             enable_on_default=True,
             help_=sv_help,
             visible=False)


@sv.on_prefix(('sx', '缩写'))
async def nbnhhsh(bot, ev: CQEvent):
    sx_origin = ev.message.extract_plain_text().strip()

    body = {
        "text": sx_origin,
    }
    r = requests.post(url, data=json.dumps(body), headers=headers, timeout=15)
    r_json = json.loads(r.text)
    suoxieList = r_json[0]
    try:
        msg = f"{sx_origin}可能是" + str(suoxieList['trans']).replace("'",
                                                                   "") + "的缩写"
        await bot.send(ev, msg)
    except:
        msg = f"没有发现缩写为{sx_origin}的,可以前往https://lab.magiconch.com/nbnhhsh/ 添加词条"
        await bot.send(ev, msg)