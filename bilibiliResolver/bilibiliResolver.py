# -*- coding: utf-8 -*-
import re
import html
import requests
from bs4 import BeautifulSoup
from aiocache import cached
from nonebot import MessageSegment as ms
from hoshino import util, Service, priv
from hoshino.typing import CQEvent, CQHttpError, Message

sv = Service('bilibiliResolver',
             manage_priv=priv.ADMIN,
             enable_on_default=True,
             visible=True,
             help_='解析bilibili',
             bundle='通用')

headers = {
    'user-agent':
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.135 Safari/537.36'
}

pattern = re.compile(
    r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
)


@cached(ttl=10)
async def get_linkSet(group_id):
    linkSet = set()
    return linkSet


#transfer b23.tv to bilibili.com
@cached(ttl=12 * 60 * 60)
async def getUrl(url):
    res = requests.get(url, timeout=15)
    url = res.url
    return url


async def getBilibiliVideoDetail(resultUrl, linkSet):
    contents = requests.get(resultUrl, headers=headers, timeout=15).text
    soup = BeautifulSoup(contents, "lxml")
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
    if link not in linkSet:
        linkSet.add(link)
        msg = [
            f"[标题]{title}", f"[作者]{auther}", f"[简介]{description}",
            f"[封面]{ms.image(imgUrl)}", f"URL:{link}"
        ]
    else:
        msg = None
    return msg


async def getBilibiliBangumiDetail(resultUrl, linkSet):
    contents = requests.get(resultUrl, headers=headers, timeout=15).text
    soup = BeautifulSoup(contents, "lxml")
    title = html.unescape(soup.title.string.replace(
        "_bilibili_哔哩哔哩", "")).replace("_", "[") + "]"
    description = html.unescape(soup.find('span', class_="absolute").text)
    imgUrl = soup.find(attrs={"property": "og:image"})['content']
    ep = re.search(r'(ss|ep)\d+', resultUrl).group()
    link = re.sub(r'(ss|ep)\d+', ep,
                  soup.find(attrs={"property": "og:url"})['content'])
    if link not in linkSet:
        linkSet.add(link)
        msg = [
            f"[标题]{title}", f"[简介]{description}", f"[封面]{ms.image(imgUrl)}",
            f"URL:{link}"
        ]
    else:
        msg = None
    return msg


@sv.on_message()
async def bilibiliResolver(bot, ev: CQEvent):
    msg = str(ev.message)
    try:
        urlList = re.findall(pattern, msg.replace("\\", ''))
    except:
        urlList = []

    if urlList != []:
        urlList = list(set(urlList))  #Initially delete repeated links
        linkSet = await get_linkSet(ev.group_id)  #avoid repeated link
        for url in urlList:
            if url.startswith("https://b23.tv") or url.startswith(
                    "https://www.bilibili.com/video/") or url.startswith(
                        "http://www.bilibili.com/video/"):
                try:
                    try:
                        msg = await getBilibiliVideoDetail(url, linkSet)
                    except:
                        msg = await getBilibiliBangumiDetail(url, linkSet)

                    try:
                        if msg != None:
                            await bot.send(ev, '\n'.join(msg))
                    except CQHttpError:
                        sv.logger.error(f"链接内容解析失败消息无法发送")
                        try:
                            await bot.send(ev, "链接内容解析失败", at_sender=True)
                        except:
                            pass
                except:
                    try:
                        await bot.send(ev, "链接内容解析失败", at_sender=True)
                    except CQHttpError:
                        sv.logger.error(f"链接内容解析失败消息无法发送")
                        try:
                            await bot.send(ev, "链接内容解析失败", at_sender=True)
                        except:
                            pass
            if url.startswith(
                    "https://www.bilibili.com/bangumi/") or url.startswith(
                        "http://www.bilibili.com/bangumi/"):
                try:
                    try:
                        msg = await getBilibiliBangumiDetail(url, linkSet)
                    except:
                        msg = await getBilibiliVideoDetail(url, linkSet)

                    try:
                        if msg != None:
                            await bot.send(ev, '\n'.join(msg))
                    except CQHttpError:
                        sv.logger.error(f"链接内容解析失败消息无法发送")
                        try:
                            await bot.send(ev, "链接内容解析失败", at_sender=True)
                        except:
                            pass
                except:
                    try:
                        await bot.send(ev, "链接内容解析失败", at_sender=True)
                    except CQHttpError:
                        sv.logger.error(f"链接内容解析失败消息无法发送")
                        try:
                            await bot.send(ev, "链接内容解析失败", at_sender=True)
                        except:
                            pass