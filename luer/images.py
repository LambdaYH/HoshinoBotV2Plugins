from . import ImageData
from migang.typing import MessageSegment as ms
from migang import R, Service

DB_PATH = R.img("luer/imagedata.db").path
Image_Data = ImageData(DB_PATH)

sv = Service("luer-images", visible=False)


@sv.on_fullmatch(("-猫娘", "/猫娘", "-miqote"))
async def get_miqote_image(bot, ev):
    img = await Image_Data._get_random_image("MIQOTE")
    await bot.send(ev, ms.image(img))


@sv.on_fullmatch(("-龙娘", "/龙娘", "-aura"))
async def get_aura_image(bot, ev):
    img = await Image_Data._get_random_image("AURA")
    await bot.send(ev, ms.image(img))


@sv.on_fullmatch(("-猫男", "/猫男", "-miqotem"))
async def get_miqotem_image(bot, ev):
    img = await Image_Data._get_random_image("MIQOTEM")
    await bot.send(ev, ms.image(img))


@sv.on_fullmatch(("-母肥", "/母肥", "-lalafell"))
async def get_lalafell_image(bot, ev):
    img = await Image_Data._get_random_image("LALAFELL")
    await bot.send(ev, ms.image(img))


@sv.on_fullmatch(("-公肥", "/公肥", "-lalafellm"))
async def get_lalafellm_image(bot, ev):
    img = await Image_Data._get_random_image("LALAFELLM")
    await bot.send(ev, ms.image(img))


@sv.on_fullmatch(("-晚安", "-meat", "/晚安"))
async def get_night_image(bot, ev):
    img = await Image_Data._get_random_image("NIGHT")
    await bot.send(ev, ms.image(img))


@sv.on_fullmatch(("-早安", "-morning", "/早安"))
async def get_morning_image(bot, ev):
    img = await Image_Data._get_random_image("MORNING")
    await bot.send(ev, ms.image(img))
