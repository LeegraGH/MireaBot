import math
import re
import vk_api
from vk_api import VkUpload
from vk_api.longpoll import VkLongPoll, VkEventType
import requests
from bs4 import BeautifulSoup
import openpyxl
import datetime
import locale
import PIL.Image as Image
from PIL.Image import Resampling
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from pathlib import Path

locale.setlocale(locale.LC_ALL, "ru")

corona_site = requests.get("https://coronavirusstat.ru/country/russia/")
corona_soup = BeautifulSoup(corona_site.text, "html.parser")
list_corona = corona_soup.findAll('div', {'class': 'col-12 p-0'})
region_corona = {}
for i in list_corona:
    reg = i.find('a').text
    site = i.find('a').get('href')
    region_corona[reg] = site

for r in region_corona:
    print(r.lower())

