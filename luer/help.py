from nonebot import on_command, CommandSession

_help = """
/晚安   晚安~
/猫娘   云吸猫娘
/猫男   云吸猫男
/早安   早安~来张獭图吧
/龙娘   云吸龙娘
/母肥   云吸母肥
/公肥   云吸公肥
""".strip()


@on_command("-help", only_to_me=False)
async def luer_help(session: CommandSession):
    await session.send(_help)
