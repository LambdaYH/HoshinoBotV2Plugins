from nonebot.exceptions import CQHttpError
from hoshino import Service, priv, util, R
from hoshino.typing import *
from nonebot import MessageSegment as ms

sv = Service('nuannuan',
             manage_priv=priv.SUPERUSER,
             enable_on_default=True,
             visible=False)


@sv.on_fullmatch(('/nn', '、nn', '/nuannuan', '、nuannuan'))
async def nuannuan(bot, ev: CQEvent):
    img_URL = ""
    msg = f"[CQ:image,cache=0,file={img_URL}]"
    try:
        await bot.send(ev, msg)
    except CQHttpError:
        sv.logger.error(f"获取暖暖作业图片失败")
        try:
            await bot.send(ev, '暖暖作业图片迷路了~', at_sender=True)
        except:
            pass
