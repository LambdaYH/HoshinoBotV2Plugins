from nonebot import on_command, CommandSession

_help = """
/晚安   晚安~
/早安   早安~来张獭图吧
/(猫男，猫娘，龙男，龙娘，人女，人男，母肥，公肥，女精，男精，鲁加男，鲁加女，兔娘，大猫)   云吸xx
""".strip()


@on_command("-help", only_to_me=False)
async def luer_help(session: CommandSession):
    await session.send(_help)
