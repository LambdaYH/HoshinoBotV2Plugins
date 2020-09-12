import os
import logging
from PIL import Image
from bs4 import BeautifulSoup
from urllib.request import urlopen
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options


def crawl_nuannuan():
    os.chdir("/root/HoshinoBot/res/img/nuannuan/")
    logging.basicConfig(
        level=logging.INFO,
        filename='nuannuan.log',
        filemode='a',
        format=
        '%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s'
    )
    options = Options()
    options.add_argument('--headless')
    driver = webdriver.Firefox(executable_path='./geckodriver',
                               options=options)
    driver.maximize_window()
    driver.set_window_size(1100, 1200)
    try:
        html = urlopen('https://www.youwanc.com/', timeout=60)
        bsObj = BeautifulSoup(html, 'lxml')
        t1 = bsObj.find_all('a')
        url = ''
        for t2 in t1:
            t3 = t2.get('href')
            if "docs.qq.com" in t3:
                url = t3
        driver.get(url)
        locator = (By.CLASS_NAME, 'operate-board')
        try:
            WebDriverWait(driver, 60,
                          0.5).until(EC.presence_of_element_located(locator))
            driver.get_screenshot_as_file("./nuannuan.png")
            crop_image = Image.open("./nuannuan.png")
            crop_image = crop_image.crop((70, 160, 800, 1100))
            crop_image.save('./nuannuan.png')
            logging.info("crawl success")
        finally:
            driver.quit()
    except:
        logging.error("urlopen timeout")
        driver.quit()


if __name__ == "__main__":
    try:
        crawl_nuannuan()
    except:
        logging.error("crawl failure")
