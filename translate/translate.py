from nonebot import on_command, CommandSession
from nonebot import permission as perm

from datetime import datetime, timedelta

from googletrans import Translator

@on_command('translate', aliases=('翻译', '翻譯', '翻訳'), permission=perm.GROUP_ADMIN, only_to_me=False)
async def translate(session: CommandSession):
    text = session.get('text')
    if text:
        try:
            translation = await get_translation(text)
            await session.send(f'机翻译文：\n{translation}')
        except:
            await session.send(f'翻译姬出错了...')
    else:
        await session.send('翻译姬待命中...')


@translate.args_parser
async def _(session: CommandSession):
    stripped_arg = session.current_arg_text.strip() # 删去首尾空白
    if stripped_arg:
        session.state['text'] = stripped_arg
    else:
        session.state['text'] = None
    return


async def get_translation(text: str) -> str:
    if not hasattr(get_translation, 'cdtime'):
        get_translation.cdtime = datetime.now() - timedelta(seconds=3)
    now = datetime.now()
    if(now < get_translation.cdtime):
        return '翻译姬冷却中...'
    else:
        get_translation.cdtime = datetime.now() + timedelta(seconds=1)
        translator = Translator()
        ret = translator.translate(text, dest='zh-CN').text
        return ret
