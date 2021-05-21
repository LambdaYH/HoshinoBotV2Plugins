import re
import html
import httpx
import asyncio
from bs4 import BeautifulSoup
from aiocache import cached
from nonebot import MessageSegment as ms
from hoshino import Service, priv
from hoshino.typing import CQEvent, CQHttpError

semaphore = asyncio.Semaphore(10)

sv = Service(
    "bilibiliResolver", manage_priv=priv.ADMIN, enable_on_default=True, visible=False
)

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36"
}

pattern = re.compile(
    r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"
)

aid_pattern = re.compile(r"(av|AV)\d+")

bvid_pattern = re.compile(r"(BV|bv)\w+")

video_keywords = (
    "https://b23.tv",
    "https://www.bilibili.com/video",
    "http://www.bilibili.com/video",
)
bangumi_keywords = (
    "https://www.bilibili.com/bangumi",
    "http://www.bilibili.com/bangumi",
)
live_keywords = ("https://live.bilibili.com", "http://live.bilibili.com")


@cached(ttl=12)
async def get_linkSet(group_id):
    linkSet = set()
    return linkSet


# transfer b23.tv to bilibili.com
@cached(ttl=60)
async def getUrl(url):
    async with httpx.AsyncClient() as client:
        res = await client.get(url, timeout=15)
    return str(res.url)


async def getContext(url):
    async with semaphore:
        async with httpx.AsyncClient() as client:
            contents = await client.get(url, headers=headers, timeout=15)
            return contents.text


async def getJson(url):
    async with semaphore:
        async with httpx.AsyncClient() as client:
            r = await client.get(url)
            return r.json()


@cached(ttl=60)
async def getBilibiliVideoDetail(resultUrl):
    if resultUrl.startswith("https://b23.tv"):
        resultUrl = await getUrl(resultUrl)
    aid = re.search(aid_pattern, resultUrl)
    bvid = re.search(bvid_pattern, resultUrl)
    url = ""
    if aid:
        url = f"https://api.bilibili.com/x/web-interface/view?aid={aid.group()[2:]}"
    elif bvid:
        url = url = f"https://api.bilibili.com/x/web-interface/view?bvid={bvid.group()}"

    details = await getJson(url)
    if details["code"] != 0:
        raise "cannot fetch video detail"
    details = details["data"]
    title = details["title"]
    description = details["desc"]
    auther = details["owner"]["name"]
    imgUrl = details["pic"]
    link = f"https://www.bilibili.com/video/{details['bvid']}"
    # get part details
    part = re.search(r"\?p=\d+", resultUrl)
    if part != None and part.group() != "?p=1":
        title += "[P" + part.group().replace("?p=", "") + "]"
        link += part.group()
    msg = [
        f"[标题] {title}",
        f"[作者] {auther}",
        f"[简介] \n{description}" if description.strip() != "" else f"[简介] {description}",
        f"[封面] {ms.image(imgUrl)}",
        f"URL:{link}",
    ]
    return msg, link


@cached(ttl=60)
async def getBilibiliBangumiDetail(resultUrl):
    text = await getContext(resultUrl)
    soup = BeautifulSoup(text, "lxml")
    title = (
        html.unescape(soup.title.string.replace("_bilibili_哔哩哔哩", "")).replace("_", "[")
        + "]"
    )
    description = html.unescape(soup.find("span", class_="absolute").text)
    imgUrl = soup.find(attrs={"property": "og:image"})["content"]
    try:
        ep = re.search(r"(ss|ep)\d+", resultUrl).group()
    except:
        if resultUrl.startswith("https://b23.tv"):
            ep = re.search(r"(ss|ep)\d+", await getUrl(resultUrl)).group()
        else:
            raise
    link = re.sub(r"(ss|ep)\d+", ep, soup.find(attrs={"property": "og:url"})["content"])
    msg = [
        f"[标题] {title}",
        f"[简介] \n{description}" if description.strip() != "" else f"[简介] {description}",
        f"[封面] {ms.image(imgUrl)}",
        f"URL:{link}",
    ]
    return msg, link


@cached(ttl=60)
async def getLiveSummary(resultUrl):
    link = re.search(r"(https|http)://live.bilibili.com/\d+", resultUrl)
    roomid = ""
    uid = ""
    title = ""
    up = ""
    imgUrl = ""
    status = ""
    if link:
        link = link.group()
        roomid = re.search(r"\d+", link).group()
    else:
        raise "no link found"

    r = await getJson(
        f"http://api.live.bilibili.com/room/v1/Room/room_init?id={roomid}"
    )
    if r["code"] == 0:
        uid = r["data"]["uid"]
    else:
        return "↑ 直播间不存在~", link
    r = await getJson(f"http://api.bilibili.com/x/space/acc/info?mid={uid}")
    if r["code"] == 0:
        title = r["data"]["live_room"]["title"]
        up = r["data"]["name"]
        imgUrl = r["data"]["live_room"]["cover"]
        status = r["data"]["live_room"]["liveStatus"]
        link = r["data"]["live_room"]["url"]
    else:
        raise "cannot fetch the detail of this live room"

    msg = [
        "[直播中]" if status == 1 else "[未开播]",
        f"[标题] {title}",
        f"[主播] {up}",
        f"[封面]{ms.image(imgUrl)}",
        f"URL:{link}",
    ]
    return msg, link


async def extractDetails(url, bot, ev, linkSet):
    url = url.rstrip("&")  # delete Animated emoticons
    if url.startswith(video_keywords):
        try:
            try:
                msg, link = await getBilibiliVideoDetail(url)
                msg = msg if link not in linkSet else None
                linkSet.add(link)
            except:
                msg, link = await getBilibiliBangumiDetail(url)
                msg = msg if link not in linkSet else None
                linkSet.add(link)

            try:
                if msg != None:
                    await bot.send(ev, "\n".join(msg))
            except CQHttpError:
                sv.logger.warning(f"解析消息发送失败")
                try:
                    await bot.send(ev, "由于风控等原因链接解析结果无法发送(如有误检测请忽略)", at_sender=True)
                except:
                    pass
        except Exception as e:
            try:
                sv.logger.warning(f"解析失败: {e}")
                await bot.send(ev, "B站内容解析失败(如有误检测请忽略)", at_sender=True)
            except CQHttpError:
                sv.logger.warning(f"B站内容解析失败消息无法发送")

    elif url.startswith(bangumi_keywords):
        try:
            try:
                msg, link = await getBilibiliBangumiDetail(url)
                msg = msg if link not in linkSet else None
                linkSet.add(link)
            except:
                msg, link = await getBilibiliVideoDetail(url)
                msg = msg if link not in linkSet else None
                linkSet.add(link)

            try:
                if msg != None:
                    await bot.send(ev, "\n".join(msg))
            except CQHttpError:
                sv.logger.warning(f"解析消息发送失败")
                try:
                    await bot.send(ev, "由于风控等原因链接解析结果无法发送(如有误检测请忽略)", at_sender=True)
                except:
                    pass
        except Exception as e:
            try:
                sv.logger.warning(f"解析失败: {e}")
                await bot.send(ev, "B站内容解析失败(如有误检测请忽略)", at_sender=True)
            except CQHttpError as e:
                sv.logger.warning(f"B站内容解析失败消息无法发送")

    elif url.startswith(live_keywords):
        try:
            msg, link = await getLiveSummary(url)
            msg = msg if link not in linkSet else None
            linkSet.add(link)

            try:
                if msg != None:
                    await bot.send(ev, "\n".join(msg))
            except CQHttpError:
                sv.logger.warning(f"解析消息发送失败")
                try:
                    await bot.send(ev, "由于风控等原因链接解析结果无法发送(如有误检测请忽略)", at_sender=True)
                except:
                    pass
        except Exception as e:
            try:
                sv.logger.warning(f"解析失败: {e}")
                await bot.send(ev, "↑ 这是一个直播间（虽然我不认识")
            except CQHttpError:
                sv.logger.warning(f"直播间概要解析失败消息无法发送")


@sv.on_message()
async def bilibiliResolver(bot, ev: CQEvent):
    msg = str(ev.message)
    try:
        urlList = re.findall(pattern, msg.replace("\\", ""))
    except:
        urlList = []

    if urlList == []:
        aid = re.search(aid_pattern, msg)
        bvid = re.search(bvid_pattern, msg)
        if aid:
            urlList.append(f"https://www.bilibili.com/video/{aid.group()}")
        if bvid:
            urlList.append(f"https://www.bilibili.com/video/{bvid.group()}")

    if urlList != []:
        urlList = list(set(urlList))  # Initially delete repeated links
        linkSet = await get_linkSet(ev.group_id)  # avoid repeated link
        tasks = [
            asyncio.create_task(extractDetails(url, bot, ev, linkSet))
            for url in urlList
        ]
        await asyncio.gather(*tasks)
