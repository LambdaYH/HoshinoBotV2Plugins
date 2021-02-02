import httpx
from hoshino import Service

headers = {
    "content-type": "application/json",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36",
}

sv_help = """
由[nhnhhsh:https://lab.magiconch.com/nbnhhsh/]驱动
使用方法: 缩写 拼音缩写
例如: 缩写 ff14
""".strip()

sv = Service("suoxie", visible=True, help_=sv_help, bundle="通用")
aliases = ("sx", "缩写", "zy", "转义", "nhnhhsh")

url = f"https://lab.magiconch.com/api/nbnhhsh/guess/"


@sv.on_prefix(aliases)
async def suoxie(bot, ev):
    try:
        episode = ev.message.extract_plain_text()
        if not episode:
            await bot.send(ev, "你想知道哪个拼音缩写的全称呢?", at_sender=True)
            return
        body = {"text": episode}
        async with httpx.AsyncClient() as client:
            r = await client.post(url=url, json=body, headers=headers, timeout=10)
        data = str((r.json())[0]["trans"]).replace("'", "")
        msg = f"{episode}可能是" + str(data) + "的缩写"
        await bot.send(ev, msg, at_sender=True)
    except:
        await bot.send(
            ev,
            f"没有发现缩写为{episode}的,可以前往https://lab.magiconch.com/nbnhhsh/ 添加词条",
            at_sender=True,
        )