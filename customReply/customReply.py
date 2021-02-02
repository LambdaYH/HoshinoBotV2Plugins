from hoshino import Service
from hoshino.priv import SUPERUSER, ADMIN, check_priv
from hoshino.typing import MessageSegment
from .__utils__ import text2img
from hoshino import logger
from nonebot import scheduler
import html
import ujson
import os

sv = Service(
    "custom_reply", manage_priv=SUPERUSER, enable_on_default=True, visible=True
)

custom_reply = {}  # do not edit it, edit it in the json instead
customReply = os.path.expanduser("~/.hoshino/customReply.json")
try:
    with open(customReply, "r", encoding="UTF-8") as json_file:
        custom_reply = ujson.load(json_file)
        if not custom_reply.get("global"):
            custom_reply["global"] = {}
except FileNotFoundError:
    if not custom_reply.get("global"):
        custom_reply["global"] = {}
    logger.warning("customReply.json not found, will create when needed.")


@sv.on_message()
async def migang_reply(bot, ev):
    msg = str(ev.message)
    group_id = str(ev.group_id)
    if custom_reply.get(group_id) and custom_reply.get(group_id).get(msg):
        await bot.send(
            ev,
            custom_reply.get(group_id)[msg]["content"],
            at_sender=custom_reply.get(group_id)[msg]["at_sender"],
        )
    elif custom_reply["global"].get(msg):
        await bot.send(
            ev,
            custom_reply["global"][msg]["content"],
            at_sender=custom_reply["global"][msg]["at_sender"],
        )
    else:
        return


@sv.on_prefix(".migangreply")
async def modify_reply(bot, ev):
    if not check_priv(ev, ADMIN):
        await bot.send(ev, "抱歉，只有群管理员才可以添加群自定义回复", at_sender=True)
    else:
        if not ev.group_id:
            await bot.finish(ev, "抱歉，自定义回复仅可在群聊中使用")
        msg = str(ev.message).strip()
        list = msg.split(" ")
        listLength = len(list)
        if listLength < 2:
            await bot.send(
                ev,
                "格式有误，请重新按照[.migangReply add/del 关键词 自定义回复 0/1(可选)]发送",
                at_sender=True,
            )
        elif listLength >= 2:
            if list[0] == "add" and not list[1].strip() == "":
                if listLength == 3:
                    if not custom_reply.get(str(ev.group_id)):
                        custom_reply[str(ev.group_id)] = {}
                    custom_reply[str(ev.group_id)][list[1]] = {
                        "content": html.unescape(list[2]),
                        "at_sender": False,
                    }
                    await bot.send(ev, f"添加关键词为[{list[1]}]的群自定义回复成功", at_sender=True)
                elif listLength == 4:
                    if not custom_reply.get(str(ev.group_id)):
                        custom_reply[str(ev.group_id)] = {}
                    custom_reply[str(ev.group_id)][list[1]] = {
                        "content": html.unescape(list[2]),
                        "at_sender": True if list[3] == "1" else False,
                    }
                    await bot.send(ev, f"添加关键词为[{list[1]}]的群自定义回复成功", at_sender=True)
                else:
                    await bot.send(
                        ev,
                        "格式有误，请重新按照[.migangReply add 关键词 自定义回复 0/1(可选)]发送",
                        at_sender=True,
                    )
            elif list[0] == "del":
                if listLength == 2:
                    if custom_reply.get(str(ev.group_id)) and custom_reply[
                        str(ev.group_id)
                    ].get(list[1]):
                        custom_reply.get(str(ev.group_id)).pop(list[1])
                        await bot.send(
                            ev,
                            f"删除关键词为[{list[1]}]的群自定义回复成功",
                            at_sender=True,
                        )
                    else:
                        await bot.send(
                            ev,
                            f"不存在关键词为[{list[1]}]的群自定义回复",
                            at_sender=True,
                        )
                else:
                    await bot.send(
                        ev, "格式有误，请重新按照[.migangReply del 关键词]发送", at_sender=True
                    )
            else:
                await bot.send(ev, "指令错误，发送 [自定义回复帮助] 查看帮助")


@sv.on_prefix(".adminreply")
async def modify_reply_admin(bot, ev):
    if not check_priv(ev, SUPERUSER):
        return
    else:
        if not ev.group_id:
            await bot.finish(ev, "抱歉，自定义回复仅可在群聊中使用")
        msg = str(ev.message).strip()
        list = msg.split(" ")
        listLength = len(list)
        if listLength < 2:
            await bot.send(
                ev,
                "格式有误，请重新按照[.adminReply add/del 关键词 自定义回复 0/1(可选)]发送",
                at_sender=True,
            )
        elif listLength >= 2:
            if list[0] == "add" and not list[1].strip() == "":
                if listLength == 3:
                    custom_reply["global"][list[1]] = {
                        "content": html.unescape(list[2]),
                        "at_sender": False,
                    }
                    await bot.send(
                        ev,
                        f"添加关键词为[{list[1]}]的全局自定义回复成功",
                        at_sender=True,
                    )
                elif listLength == 4:
                    custom_reply["global"][list[1]] = {
                        "content": html.unescape(list[2]),
                        "at_sender": True if list[3] == "1" else False,
                    }
                    await bot.send(
                        ev,
                        f"添加关键词为[{list[1]}]的全局自定义回复成功",
                        at_sender=True,
                    )
                else:
                    await bot.send(
                        ev,
                        "格式有误，请重新按照[.adminReply add 关键词 0/1(可选)]发送",
                        at_sender=True,
                    )
            elif list[0] == "del":
                if listLength == 2:
                    if custom_reply.get("global").get(list[1]):
                        custom_reply.get("global").pop(list[1])
                        await bot.send(
                            ev,
                            f"删除关键词为[{list[1]}]的全局自定义回复成功",
                            at_sender=True,
                        )
                    else:
                        await bot.send(
                            ev,
                            f"不存在关键词为[{list[1]}]的全局自定义回复",
                            at_sender=True,
                        )
                else:
                    await bot.send(
                        ev, "格式有误，请重新按照[.adminReply del 自定义回复]发送", at_sender=True
                    )
            else:
                await bot.send(ev, "指令错误，发送 [自定义回复帮助] 查看帮助")


@sv.on_fullmatch("自定义回复帮助")
async def migang_reply_help(bot, ev):
    msg = """
[添加群自定义回复]
  [基础]
  .migangreply add 关键词 自定义回复
  [进阶]
  .migangreply add 关键词 自定义回复 0 (在回复时不at对方, 最后参数默认为0)
  .migangreply add 关键词 自定义回复 1 (在回复时at对方)
[删除群自定义回复]
.migangreply del 关键词
[查看自定义回复]
米缸查看自定义回复
[Tips]
图片请不要直接使用粘贴方式设定自定义回复，否则未来会失效，建议采用图床上传图片
类似([CQ:image,file=https://image.cinte.cc/2021/01/24/886d904a65e51.png])
如不嫌弃可以使用(https://image.cinte.cc/)作为图床
(群自定义回复优先级高于维护者设定的全局自定义回复, 仅在群聊中可使用自定义回复)
""".strip()

    await bot.send(ev, MessageSegment.image(text2img(msg)))


@sv.on_fullmatch("查看自定义回复", only_to_me=True)
async def show_custom_reply(bot, ev):
    if not ev.group_id:
        await bot.finish(ev, "抱歉，自定义回复仅可在群聊中使用")
    msg = "[本群自定义回复]\n"
    if custom_reply.get(str(ev.group_id)):
        for key in custom_reply.get(str(ev.group_id)):
            msg += f"{html.unescape(key)}: {custom_reply.get(str(ev.group_id))[key]['content']}\n"
    else:
        msg += "无\n"
    msg += "[全局自定义回复]\n"
    for key in custom_reply.get("global"):
        msg += f"{html.unescape(key)}: {custom_reply.get('global')[key]['content']}\n"

    await bot.send(ev, MessageSegment.image(text2img(msg)))


async def saveCustomReply():
    try:
        with open(customReply, "w", encoding="UTF-8") as json_file:
            json_file.write(ujson.dumps(custom_reply))
            logger.info("customReply has been saved")
    except FileNotFoundError:
        raise "customReply.json not found, will create when needed."


@scheduler.scheduled_job("interval", seconds=600)
async def saveData():
    await saveCustomReply()
