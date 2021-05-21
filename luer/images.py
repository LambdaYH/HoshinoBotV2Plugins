from . import ImageData
from hoshino.typing import MessageSegment as ms
from hoshino import R, Service
import random

DB_PATH = R.img("luer/imagedata.db").path
Image_Data = ImageData(DB_PATH)

sv = Service("luer-images", visible=False)


@sv.on_fullmatch(("-猫男", "/猫男", "-miqotem"))
async def get_miqotem_image(bot, ev):
    img = await Image_Data._get_random_image("MIQOTEM")
    await bot.send(ev, ms.image(img))


@sv.on_fullmatch(("-猫娘", "/猫娘", "-miqote"))
async def get_miqote_image(bot, ev):
    img = await Image_Data._get_random_image("MIQOTE")
    await bot.send(ev, ms.image(img))


@sv.on_fullmatch(("-龙娘", "/龙娘", "-aura"))
async def get_aura_image(bot, ev):
    img = await Image_Data._get_random_image("AURA")
    await bot.send(ev, ms.image(img))


@sv.on_fullmatch(("-龙男", "/龙男", "-auram"))
async def get_auram_image(bot, ev):
    img = await Image_Data._get_random_image("AURAM")
    await bot.send(ev, ms.image(img))


@sv.on_fullmatch(("-人女", "/人娘", "-hyur", "/人女", "-人娘"))
async def get_hyur_image(bot, ev):
    img = await Image_Data._get_random_image("HYUR")
    await bot.send(ev, ms.image(img))


@sv.on_fullmatch(("-人男", "/人男", "-hyurm"))
async def get_hyurm_image(bot, ev):
    img = await Image_Data._get_random_image("HYURM")
    await bot.send(ev, ms.image(img))


@sv.on_fullmatch(("-母肥", "/母肥", "-lalafell"))
async def get_lalafell_image(bot, ev):
    img = await Image_Data._get_random_image("LALAFELL")
    await bot.send(ev, ms.image(img))


@sv.on_fullmatch(("-公肥", "/公肥", "-lalafellm"))
async def get_lalafellm_image(bot, ev):
    img = await Image_Data._get_random_image("LALAFELLM")
    await bot.send(ev, ms.image(img))


@sv.on_fullmatch(("-女精", "/女精", "-elezen", "-女精灵", "/女精灵"))
async def get_elezen_image(bot, ev):
    img = await Image_Data._get_random_image("ELEZEN")
    await bot.send(ev, ms.image(img))


@sv.on_fullmatch(("-男精", "/男精", "-elezenm", "-男精灵", "/男精灵"))
async def get_elezenm_image(bot, ev):
    img = await Image_Data._get_random_image("ELEZENM")
    await bot.send(ev, ms.image(img))


@sv.on_fullmatch(("-鲁家女", "/鲁家女", "-roegadyn", "-鲁加女", "/鲁加女"))
async def get_roegadyn_image(bot, ev):
    img = await Image_Data._get_random_image("ROEGADYN")
    await bot.send(ev, ms.image(img))


@sv.on_fullmatch(("-鲁家男", "/鲁家男", "-roegadynm", "-鲁加男", "/鲁加男"))
async def get_roegadynm_image(bot, ev):
    img = await Image_Data._get_random_image("ROEGADYNM")
    await bot.send(ev, ms.image(img))


@sv.on_fullmatch(("-兔娘", "/兔娘", "-viera"))
async def get_viera_image(bot, ev):
    img = await Image_Data._get_random_image("VIERA")
    await bot.send(ev, ms.image(img))


@sv.on_fullmatch(("-大猫", "/大猫", "-hrothgar"))
async def get_hrothgar_image(bot, ev):
    img = await Image_Data._get_random_image("HROTHGAR")
    await bot.send(ev, ms.image(img))


@sv.on_fullmatch(("-拉拉肥", "/拉拉肥", "-肥肥", "/肥肥"))
async def get_lalafell_all_image(bot, ev):
    if random.random() < 0.50:
        img = await Image_Data._get_random_image("LALAFELL")
    else:
        img = await Image_Data._get_random_image("LALAFELLM")
    await bot.send(ev, ms.image(img))


@sv.on_fullmatch(("-猫魅", "/猫魅", "-猫魅族", "/猫魅族", "-猫猫", "/猫猫"))
async def get_miqote_all_image(bot, ev):
    if random.random() < 0.50:
        img = await Image_Data._get_random_image("MIQOTE")
    else:
        img = await Image_Data._get_random_image("MIQOTEM")
    await bot.send(ev, ms.image(img))


@sv.on_fullmatch(("-鲁家", "/鲁家", "-鲁加", "/鲁加"))
async def get_roegadyn_all_image(bot, ev):
    if random.random() < 0.50:
        img = await Image_Data._get_random_image("ROEGADYN")
    else:
        img = await Image_Data._get_random_image("ROEGADYNM")
    await bot.send(ev, ms.image(img))


@sv.on_fullmatch(("-晚安", "-meat", "/晚安"))
async def get_night_image(bot, ev):
    img = await Image_Data._get_random_image("NIGHT")
    await bot.send(ev, ms.image(img))


@sv.on_fullmatch(("-早安", "-morning", "/早安"))
async def get_morning_image(bot, ev):
    img = await Image_Data._get_random_image("MORNING")
    await bot.send(ev, ms.image(img))
