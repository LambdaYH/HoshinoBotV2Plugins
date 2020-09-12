import os
import random
from datetime import datetime
from hoshino import Service, priv, util, R
from hoshino.typing import CQEvent, CQHttpError
from hoshino.config import EorzeaZhanbu as cfg

occupation = cfg.occupation
dye = cfg.dye
event = cfg.event
luckYiReply = cfg.luckYiReply
luckJiReply = cfg.luckJiReply

sv = Service('EorzeaZhanbu',
             manage_priv=priv.SUPERUSER,
             enable_on_default=True,
             visible=True)


@sv.on_fullmatch(('/占卜', '、占卜'))
async def zhanbu(bot, ev: CQEvent):
    random.seed(datetime.now().strftime('%d') + str(ev.user_id) +
                datetime.now().strftime('%m%Y'))
    luck = int(random.randint(0, 100))

    random.seed(datetime.now().strftime('%m') + str(ev.user_id) +
                datetime.now().strftime('%d%Y'))
    luckOccupation = occupation[random.randint(0, len(occupation) - 1)]

    random.seed(datetime.now().strftime('%Y') + str(ev.user_id) +
                datetime.now().strftime('%d%m'))
    luckDye = dye[random.randint(0, len(dye) - 1)]

    random.seed(datetime.now().strftime('%d%m%Y') + str(ev.user_id) +
                datetime.now().strftime('%Y%m%d'))
    luckYi = event[random.randint(0, len(event) - 1)]

    random.seed(datetime.now().strftime('%d%m%Y') +
                datetime.now().strftime('%Y%m%d') + str(ev.user_id))
    luckJi = event[random.randint(0, len(event) - 1)]
    repeatCount = 0
    while luckYi == luckJi:
        random.seed(datetime.now().strftime('%d%m%Y') + str(repeatCount) +
                    datetime.now().strftime('%Y%m%d') + str(ev.user_id))
        luckJi = event[random.randint(0, len(event) - 1)]
        repeatCount += 1
    appendMsg = ''
    if (luck > 94):
        appendMsg = "是欧皇(*′▽｀)ノノ"
    elif (luck < 6):
        appendMsg = "是非酋︿(￣︶￣)︿" + str(R.img('zhanbu/', 'feiqiu.jpg').cqcode)
    elif (luckOccupation == "占星" and luck >= 80):
        appendMsg = "米缸掐指一算，你今天的占卜覆盖率一定特别高！"
    elif (luckOccupation == "占星" and luck < 10):
        appendMsg = "米缸掐指一算，你今天刷不出来三段占卜了"
    elif (luckOccupation == "占星" and luck > 29 and luck < 80):
        appendMsg = "米缸掐指一算，今天轮到你放LB了"
    elif (luckYiReply.get(luckYi) != None and luckJiReply.get(luckJi) != None):
        random.seed(datetime.now().strftime('%d') + str(ev.user_id) +
                    datetime.now().strftime('%d%m%Y%d'))
        if (random.randint(0, 1) == 0):
            for i in luckYiReply.get(luckYi):
                if (i.startswith("img:")):
                    filename = i.replace("img:", "")
                    appendMsg = appendMsg + str(
                        R.img('zhanbu/', filename).cqcode)
                else:
                    appendMsg = appendMsg + i
        else:
            for i in luckJiReply.get(luckJi):
                if (i.startswith("img:")):
                    filename = i.replace("img:", "")
                    appendMsg = appendMsg + str(
                        R.img('zhanbu/', filename).cqcode)
                else:
                    appendMsg = appendMsg + i
    elif (luckYiReply.get(luckYi) != None):
        for i in luckYiReply.get(luckYi):
            if (i.startswith("img:")):
                filename = i.replace("img:", "")
                appendMsg = appendMsg + str(R.img('zhanbu/', filename).cqcode)
            else:
                appendMsg = appendMsg + i
    elif (luckJiReply.get(luckJi) != None):
        for i in luckJiReply.get(luckJi):
            if (i.startswith("img:")):
                filename = i.replace("img:", "")
                appendMsg = appendMsg + str(R.img('zhanbu/', filename).cqcode)
            else:
                appendMsg = appendMsg + i

    msg = [
        f"\n运势：{luck}% 幸运职业：{luckOccupation}", f"推荐染剂：{luckDye}",
        f"宜：{luckYi} 忌：{luckJi}", f"{appendMsg}"
    ]
    try:
        await bot.send(ev, '\n'.join(msg), at_sender=True)
    except CQHttpError:
        sv.logger.error(f"占卜失败")
        try:
            await bot.send(ev, '占卜水晶球破碎了~', at_sender=True)
        except:
            pass
