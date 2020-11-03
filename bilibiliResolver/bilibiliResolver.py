# -*- coding: utf-8 -*-
import re
import html
from bs4 import BeautifulSoup
from aiocache import cached
from nonebot import MessageSegment as ms
from hoshino import util, Service, priv, aiorequests
from hoshino.typing import CQEvent, CQHttpError, Message

sv = Service('bilibiliResolver',
             manage_priv=priv.ADMIN,
             enable_on_default=True,
             visible=False)

headers = {
    'user-agent':
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.135 Safari/537.36'
}

pattern = re.compile(
    r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
)

aid_pattern = re.compile(r'(av|AV)\d+')

bvid_pattern = re.compile(r'(BV|bv)\w+')

video_keywords = ('https://b23.tv', 'https://www.bilibili.com/video',
                  'http://www.bilibili.com/video')
bangumi_keywords = ('https://www.bilibili.com/bangumi',
                    'http://www.bilibili.com/bangumi')
live_keywords = ('https://live.bilibili.com', 'http://live.bilibili.com')


@cached(ttl=12)
async def get_linkSet(group_id):
    linkSet = set()
    return linkSet


#transfer b23.tv to bilibili.com
@cached(ttl=60)
async def getUrl(url):
    res = await aiorequests.get(url, timeout=15)
    return res.url


@cached(ttl=60)
async def getBilibiliVideoDetail(resultUrl):
    contents = await aiorequests.get(resultUrl, headers=headers, timeout=15)
    soup = BeautifulSoup((await contents.text), "lxml")
    title = html.unescape(
        soup.find(attrs={"name": "title"})['content']).replace(
            "_哔哩哔哩 (゜-゜)つロ 干杯~-bilibili", "")
    description = html.unescape(soup.find('div', class_="info open").text)
    auther = html.unescape(soup.find(attrs={"name": "author"})['content'])
    imgUrl = soup.find(attrs={"itemprop": "image"})['content']
    #get part details
    if resultUrl.startswith("https://b23.tv"):
        part = re.search(r"\?p=\d+", await getUrl(resultUrl))
    else:
        part = re.search(r"\?p=\d+", resultUrl)
    if part != None and part.group() != "?p=1":
        title += "[P" + part.group().replace("?p=", "") + "]"
        link = soup.find(
            attrs={"itemprop": "url"})['content'][:-1] + part.group()
    else:
        link = soup.find(attrs={"itemprop": "url"})['content']
    msg = [
        f"[标题]{title}", f"[作者]{auther}", f"[简介]{description}",
        f"[封面]{ms.image(imgUrl)}", f"URL:{link}"
    ]
    return msg, link


@cached(ttl=60)
async def getBilibiliBangumiDetail(resultUrl):
    contents = await aiorequests.get(resultUrl, headers=headers, timeout=15)
    soup = BeautifulSoup((await contents.text), "lxml")
    title = html.unescape(soup.title.string.replace(
        "_bilibili_哔哩哔哩", "")).replace("_", "[") + "]"
    description = html.unescape(soup.find('span', class_="absolute").text)
    imgUrl = soup.find(attrs={"property": "og:image"})['content']
    ep = re.search(r'(ss|ep)\d+', resultUrl).group()
    link = re.sub(r'(ss|ep)\d+', ep,
                  soup.find(attrs={"property": "og:url"})['content'])
    msg = [
        f"[标题]{title}", f"[简介]{description}", f"[封面]{ms.image(imgUrl)}",
        f"URL:{link}"
    ]
    return msg, link


@cached(ttl=60)
async def getLiveSummary(resultUrl):
    contents = await aiorequests.get(resultUrl, headers=headers, timeout=15)
    soup = BeautifulSoup((await contents.text), "lxml")
    summarys = str(html.unescape(soup.find(
        'title', id="link-app-title").text)).split("-")[:2]
    title = summarys[0].strip()
    up = summarys[1].strip()
    link = re.search(r'(https|http)://live.bilibili.com/\d+', resultUrl)
    if link:
        link = link.group()
    msg = [f"[直播间]", f"[标题]{title}", f"[up]{up}", f"URL:{link}"]
    return msg, link


@sv.on_message()
async def bilibiliResolver(bot, ev: CQEvent):
    msg = str(ev.message)
    try:
        urlList = re.findall(pattern, msg.replace("\\", ''))
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
        urlList = list(set(urlList))  #Initially delete repeated links
        linkSet = await get_linkSet(ev.group_id)  #avoid repeated link
        for url in urlList:
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
                            await bot.send(ev, '\n'.join(msg))
                    except CQHttpError:
                        sv.logger.error(f"解析消息发送失败")
                        try:
                            await bot.send(ev,
                                           "由于风控等原因链接解析结果无法发送",
                                           at_sender=True)
                        except:
                            pass
                except:
                    try:
                        await bot.send(ev, "链接/av号/bv号内容解析失败", at_sender=True)
                    except CQHttpError:
                        sv.logger.error(f"链接/av号/bv号内容解析失败消息无法发送")
                        try:
                            await bot.send(ev,
                                           "链接/av号/bv号内容解析失败",
                                           at_sender=True)
                        except:
                            pass
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
                            await bot.send(ev, '\n'.join(msg))
                    except CQHttpError:
                        sv.logger.error(f"解析消息发送失败")
                        try:
                            await bot.send(ev,
                                           "由于风控等原因链接解析结果无法发送",
                                           at_sender=True)
                        except:
                            pass
                except:
                    try:
                        await bot.send(ev, "链接/av号/bv号内容解析失败", at_sender=True)
                    except CQHttpError:
                        sv.logger.error(f"链接/av号/bv号内容解析失败消息无法发送")
                        try:
                            await bot.send(ev,
                                           "链接/av号/bv号内容解析失败",
                                           at_sender=True)
                        except:
                            pass
            elif url.startswith(live_keywords):
                try:
                    msg, link = await getLiveSummary(url)
                    msg = msg if link not in linkSet else None
                    linkSet.add(link)

                    try:
                        if msg != None:
                            await bot.send(ev, '\n'.join(msg))
                    except CQHttpError:
                        sv.logger.error(f"解析消息发送失败")
                        try:
                            await bot.send(ev,
                                           "由于风控等原因链接解析结果无法发送",
                                           at_sender=True)
                        except:
                            pass
                except:
                    try:
                        await bot.send(ev, "直播间概要解析失败", at_sender=True)
                    except CQHttpError:
                        sv.logger.error(f"直播间概要解析失败消息无法发送")
                        try:
                            await bot.send(ev, "直播间概要解析失败", at_sender=True)
                        except:
                            pass
