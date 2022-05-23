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

table = ""
teacher_table = ""
group = ""
teacher = ""
safeGroup = ""
nameDays = ["понедельник", "вторник", "среда", "четверг", "пятница", "суббота", "воскресенье"]
weekday = {1: "понедельник", 2: 'вторник', 3: 'среда', 4: 'четверг', 5: 'пятница', 6: 'суббота', 7: 'воскресенье'}
last_message = ""
ras = ""
region_corona = {}

# Время
today = datetime.date.today().strftime("%a").lower()
tomorrow = (datetime.date.today() + datetime.timedelta(days=1)).strftime("%a").lower()
thisWeek = datetime.date.today() - datetime.timedelta(days=datetime.date.today().weekday())
nextWeek = (datetime.date.today() + datetime.timedelta(weeks=1) - datetime.timedelta(
    days=datetime.date.today().weekday()))

# API-ключ
token = "58549c03604a0c74ad92e0c1eda3b02a2481ec5fb1e103222779863a1aa208540679f0c56a906f13870a9"

# Авторизация как сообщества
vk_session = vk_api.VkApi(token=token)
vk = vk_session.get_api()

upload = VkUpload(vk_session)

# Работа с сообщениями
longpoll = VkLongPoll(vk_session)

# Клавиатура
keyboard = VkKeyboard(one_time=True)
keyboard.add_button("на сегодня", color=VkKeyboardColor.POSITIVE)
keyboard.add_button("на завтра", color=VkKeyboardColor.NEGATIVE)
keyboard.add_line()
keyboard.add_button("на эту неделю", color=VkKeyboardColor.PRIMARY)
keyboard.add_button("на следующую неделю", color=VkKeyboardColor.PRIMARY)
keyboard.add_line()
keyboard.add_button("какая неделя?", color=VkKeyboardColor.SECONDARY)
keyboard.add_button("какая группа?", color=VkKeyboardColor.SECONDARY)

weatherKeyboard = VkKeyboard(one_time=True)
weatherKeyboard.add_button("сейчас", color=VkKeyboardColor.PRIMARY)
weatherKeyboard.add_button("сегодня", color=VkKeyboardColor.POSITIVE)
weatherKeyboard.add_button("завтра", color=VkKeyboardColor.POSITIVE)
weatherKeyboard.add_line()
weatherKeyboard.add_button("на 5 дней", color=VkKeyboardColor.POSITIVE)

keyboard1 = VkKeyboard(one_time=True)
keyboard1.add_button("на сегодня", color=VkKeyboardColor.POSITIVE)
keyboard1.add_button("на завтра", color=VkKeyboardColor.NEGATIVE)
keyboard1.add_line()
keyboard1.add_button("на эту неделю", color=VkKeyboardColor.PRIMARY)
keyboard1.add_button("на следующую неделю", color=VkKeyboardColor.PRIMARY)

# Какая неделя?
weekStudy = int(datetime.date.today().strftime("%V")) - int(datetime.date(2022, 2, 9).strftime("%V")) + 1


# Неделя по дате
def numWeek(d=datetime.date.today()):
    return int(d.strftime("%V")) - int(datetime.date(2022, 2, 9).strftime("%V")) + 1


# четность недели
def getParity(weekStudy):
    if weekStudy % 2 == 0:
        return 0
    else:
        return 1


def changeMonth(m):
    out = ''
    if m == 'январь':
        out = 'января'
    elif m == 'декабрь':
        out = 'декабря'
    elif m == 'февраль':
        out = 'февраля'
    elif m == 'март':
        out = 'марта'
    elif m == 'апрель':
        out = 'апреля'
    elif m == 'май':
        out = 'мая'
    elif m == 'июнь':
        out = 'июня'
    elif m == 'июль':
        out = 'июля'
    elif m == 'август':
        out = 'августа'
    elif m == 'сентябрь':
        out = 'сентябрь'
    elif m == 'октябрь':
        out = 'октября'
    elif m == 'ноябрь':
        out = 'ноября'
    elif m == 'декабрь':
        out = 'декабря'
    return out


def typeWind(wind):
    if 0 <= wind < 0.3:
        return "штиль"
    elif 0.3 <= wind < 1.6:
        return "тихий"
    elif 1.6 <= wind < 3.4:
        return "лёгкий"
    elif 3.4 <= wind < 5.5:
        return "слабый"
    elif 5.5 <= wind < 8:
        return "умеренный"
    elif 8 <= wind < 10.8:
        return "свежий"
    elif 10.8 <= wind < 13.9:
        return "сильный"
    elif 13.9 <= wind < 17.2:
        return "крепкий"
    elif 17.2 <= wind < 20.8:
        return "очень крепкий"
    elif 20.8 <= wind < 24.5:
        return "шторм"
    elif 24.5 <= wind < 28.5:
        return "сильный шторм"
    elif 28.5 <= wind < 33:
        return "жестокий шторм"
    else:
        return "ураган"


def wayWind(deg):
    if 0 <= deg < 45:
        return "северный"
    elif 45 <= deg < 90:
        return "северо-восточный"
    elif 90 <= deg < 135:
        return "восточный"
    elif 135 <= deg < 180:
        return "юго-восточный"
    elif 180 <= deg < 225:
        return "южный"
    elif 225 <= deg < 270:
        return "юго-западный"
    elif 270 <= deg < 315:
        return "западный"
    else:
        return "северо-западный"


def setCourse(group):
    if datetime.date.today().month in [9, 10, 11, 12]:
        if int(group[8:]) == datetime.date.today().year:
            return 1
        elif int(datetime.date.today().strftime("%y")) - int(group[8:]) == 1:
            return 2
        else:
            return 3
    else:
        if int(datetime.date.today().strftime("%y")) - int(group[8:]) == 1:
            return 1
        elif int(datetime.date.today().strftime("%y")) - int(group[8:]) == 2:
            return 2
        else:
            return 3


# Расписание с сайта
page = requests.get("https://www.mirea.ru/schedule/")
soup = BeautifulSoup(page.text, "html.parser")

result = soup.find('div', {'class': 'rasspisanie'}).find(string="Институт информационных технологий").find_parent(
    'div').find_parent('div').findAll(href=re.compile('https://'))[:3]

result1 = result[0].get('href')
result2 = result[1].get('href')
result3 = result[2].get('href')
f1 = open("file" + str(1) + ".xlsx", "wb")
f2 = open("file" + str(2) + ".xlsx", "wb")
f3 = open("file" + str(3) + ".xlsx", "wb")
resp1 = requests.get(result1)
resp2 = requests.get(result2)
resp3 = requests.get(result3)
f1.write(resp1.content)
f2.write(resp2.content)
f3.write(resp3.content)
book1 = openpyxl.load_workbook("file" + str(1) + ".xlsx")
book2 = openpyxl.load_workbook("file" + str(2) + ".xlsx")
book3 = openpyxl.load_workbook("file" + str(3) + ".xlsx")
sheet1 = book1.active
sheet2 = book2.active
sheet3 = book3.active
allSheet = [sheet1, sheet2, sheet3]


# Расписание группы
def groupTimetable(date):
    global table
    global group
    dayWeek = ['пн', 'вт', 'ср', 'чт', 'пт', 'сб']
    num_cols = sheet.max_column
    for k in range(1, num_cols):
        if sheet.cell(row=2, column=k).value == group:
            num = 1
            if date == dayWeek[0]:
                diapason = sheet.iter_rows(min_row=4, max_row=15, min_col=k, max_col=k + 3)
            elif date == dayWeek[1]:
                diapason = sheet.iter_rows(min_row=16, max_row=27, min_col=k, max_col=k + 3)
            elif date == dayWeek[2]:
                diapason = sheet.iter_rows(min_row=28, max_row=39, min_col=k, max_col=k + 3)
            elif date == dayWeek[3]:
                diapason = sheet.iter_rows(min_row=40, max_row=51, min_col=k, max_col=k + 3)
            elif date == dayWeek[4]:
                diapason = sheet.iter_rows(min_row=52, max_row=63, min_col=k, max_col=k + 3)
            else:
                diapason = sheet.iter_rows(min_row=64, max_row=75, min_col=k, max_col=k + 3)

            parity = getParity(weekStudy)
            if parity == 0:
                m = 0
                for row in diapason:
                    if m % 2 == 0:
                        m += 1
                        continue
                    table += str(num) + ") "
                    num += 1
                    for cell in row:
                        if cell.value is None or cell.value.upper() == cell.value.lower():
                            table += '-\n'
                            break
                        else:
                            if row[-1] != cell:
                                table += cell.value + ", "
                            else:
                                table += cell.value + '\n'
                    m += 1
            elif parity == 1:
                m = 0
                for row in diapason:
                    if m % 2 != 0:
                        m += 1
                        continue
                    table += str(num) + ") "
                    num += 1
                    for cell in row:
                        if cell.value is None or cell.value.upper() == cell.value.lower():
                            table += '-\n'
                            break
                        else:
                            if row[-1] != cell:
                                table += cell.value + ", "
                            else:
                                table += cell.value + '\n'
                    m += 1
    if table == "":
        group = ""


# Поиск преподавателя
def searchTeacher(teacher):
    p = 1
    same_teachers = []
    for sheet in allSheet:
        num_cols = sheet.max_column
        num_rows = sheet.max_row
        for j in range(1, num_cols):
            if sheet.cell(row=3, column=j).value == "ФИО преподавателя":
                for h in range(4, num_rows):
                    if sheet.cell(row=h, column=j).value is not None:
                        if '\n' in str(sheet.cell(row=h, column=j).value):
                            temp_teachers = str(sheet.cell(row=h, column=j).value).split('\n')
                        else:
                            temp_teachers = str(sheet.cell(row=h, column=j).value).split(', ')
                        for v in temp_teachers:
                            if v[:-5] == teacher and v not in same_teachers:
                                same_teachers.append(v)
                            elif "." not in v and v == teacher and v not in same_teachers:
                                same_teachers.append(v)
        p += 1
    return same_teachers


# Расписание преподавателя
def teacherTimetable(teacher):
    global weekday
    rasp = [{}, {}]
    for i in range(2):
        for j in range(6):
            rasp[i][weekday[j + 1]] = ['-'] * 6
    for sheet in allSheet:
        num_cols = sheet.max_column
        num_rows = sheet.max_row
        for i in range(1, num_cols + 1):
            if sheet.cell(row=3, column=i).value == "ФИО преподавателя":
                for j in range(3, num_rows + 1):
                    if sheet.cell(row=j, column=i).value is not None:
                        if '\n' in str(sheet.cell(row=j, column=i).value):
                            var = str(sheet.cell(row=j, column=i).value).split('\n')
                        else:
                            var = str(sheet.cell(row=j, column=i).value).split(', ')
                        for k in range(len(var)):
                            if teacher.lower() == var[k].lower().strip().lstrip():
                                num_day = weekday[(j - 4) // 12 + 1]
                                num_w = j % 2
                                num_p = ((j - 4) % 12) // 2
                                group = str(sheet.cell(row=2, column=i - 2).value)
                                if rasp[num_w][num_day][num_p] != '-':
                                    rasp[num_w][num_day][num_p] = rasp[num_w][num_day][num_p] + ", " + group
                                else:
                                    try:
                                        rasp[num_w][num_day][num_p] = group
                                        if str(sheet.cell(row=j, column=i - 1).value).split('\n')[k] is not None:
                                            rasp[num_w][num_day][num_p] = \
                                                str(sheet.cell(row=j, column=i - 1).value).split('\n')[k] + ", " + \
                                                rasp[num_w][num_day][num_p]
                                        if str(sheet.cell(row=j, column=i + 1).value).split('\n')[k] is not None:
                                            rasp[num_w][num_day][num_p] = \
                                                str(sheet.cell(row=j, column=i + 1).value).split('\n')[k] + ", " + \
                                                rasp[num_w][num_day][num_p]
                                        rasp[num_w][num_day][num_p] = str(
                                            sheet.cell(row=j, column=i - 2).value.split('\n')[k]) + ", " + \
                                                                      rasp[num_w][num_day][num_p]
                                    except IndexError:
                                        rasp[num_w][num_day][num_p] = group
                                        if str(sheet.cell(row=j, column=i - 1).value) is not None:
                                            rasp[num_w][num_day][num_p] = str(
                                                sheet.cell(row=j, column=i - 1).value) + ", " + rasp[num_w][num_day][
                                                                              num_p]
                                        if str(sheet.cell(row=j, column=i + 1).value) is not None:
                                            rasp[num_w][num_day][num_p] = str(
                                                sheet.cell(row=j, column=i + 1).value) + ", " + rasp[num_w][num_day][
                                                                              num_p]
                                        rasp[num_w][num_day][num_p] = str(
                                            sheet.cell(row=j, column=i - 2).value) + ", " + rasp[num_w][num_day][num_p]
    return rasp


# Работа бота
for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW:
        if event.to_me:
            message = event.text.lower()
            add_message = event.text
            id = event.user_id
            if message == "начать":
                vk_session.method('messages.send', {'user_id': id, 'sticker_id': 8801, 'random_id': 0})
                vk_session.method('messages.send',
                                  {'user_id': id,
                                   'message': 'Список доступных команд:\n1) Начать - посмотреть список доступных команд\n\
2) Бот - расписание для группы (формат группы - ИКБО-08-21)\n\
3) Найти <фамилия преподавателя> - расписание для преподавателя\n\
4) Погода - погода в Москве\n\
5) Корона - статистика по коронавирусу в России\n\
6) Корона <название региона> - статистика по коронавирусу в указанном регионе',
                                   'random_id': 0})
            elif re.search(r'[а-яА-Я]{4}-\d{2}-\d{2}', message) is not None and len(message) == 10:
                last_message = ""
                group = message.upper()
                safeGroup = group
                vk_session.method('messages.send',
                                  {'user_id': id, 'message': "Я запомнил, что вы из группы " + group, 'random_id': 0})
                course = setCourse(group)
                sheet = allSheet[course-1]
            elif message == "бот":
                last_message = ""
                if group != "":
                    vk_session.method('messages.send', {'user_id': id, 'message': "Показать расписание группы " + group,
                                                        'keyboard': keyboard.get_keyboard(), 'random_id': 0})
                else:
                    vk_session.method('messages.send',
                                      {'user_id': id, 'message': "Вы не уточнили группу!", 'random_id': 0})
            elif message == "какая неделя?":
                last_message = ""
                vk_session.method('messages.send',
                                  {'user_id': id, 'message': "Идет " + str(weekStudy) + " неделя", 'random_id': 0})
            elif message == "какая группа?":
                last_message = ""
                group = safeGroup
                if group != "":
                    vk_session.method('messages.send',
                                      {'user_id': id, 'message': "Показываю расписание группы " + group,
                                       'random_id': 0})
                else:
                    vk_session.method('messages.send',
                                      {'user_id': id, 'message': "Вы не уточнили группу!", 'random_id': 0})
            elif message == "на сегодня" and last_message == "":
                if group == "":
                    vk_session.method('messages.send',
                                      {'user_id': id, 'message': "Вы не уточнили группу!", 'random_id': 0})
                elif today == "вс":
                    vk_session.method('messages.send',
                                      {'user_id': id, 'message': "Выходной :)",
                                       'random_id': 0})
                    vk_session.method('messages.send',
                                      {'user_id': id, 'sticker_id': 8797, 'random_id': 0})
                else:
                    groupTimetable(today)
                    if group == "":
                        vk_session.method('messages.send',
                                          {'user_id': id,
                                           'message': "В расписании нет такой группы! Попробуйте ввести другую группу.",
                                           'random_id': 0})
                    else:
                        month = datetime.date.today().strftime("%B").lower()
                        month = changeMonth(month)
                        table = "Расписание на " + datetime.date.today().strftime("%d") + " " + month + "\n" + table
                        vk_session.method('messages.send', {'user_id': id, 'message': table, 'random_id': 0})
                        table = ""
                group = safeGroup
            elif message == "на завтра" and last_message == "":
                if group == "":
                    vk_session.method('messages.send',
                                      {'user_id': id, 'message': "Вы не уточнили группу!", 'random_id': 0})
                elif tomorrow == "вс":
                    vk_session.method('messages.send',
                                      {'user_id': id, 'message': "Выходной :)",
                                       'random_id': 0})
                    vk_session.method('messages.send',
                                      {'user_id': id, 'sticker_id': 8797, 'random_id': 0})
                else:
                    if tomorrow == "пн":
                        weekStudy += 1
                    groupTimetable(tomorrow)
                    if group == "":
                        vk_session.method('messages.send',
                                          {'user_id': id,
                                           'message': "В расписании нет такой группы! Попробуйте ввести другую группу.",
                                           'random_id': 0})
                    else:
                        month = (datetime.date.today() + datetime.timedelta(days=1)).strftime("%B").lower()
                        month = changeMonth(month)
                        table = "Расписание на " + (datetime.date.today() + datetime.timedelta(days=1)).strftime(
                            "%d") + " " + month + "\n" + table
                        vk_session.method('messages.send', {'user_id': id, 'message': table, 'random_id': 0})
                        table = ""
                    if tomorrow == "пн":
                        weekStudy -= 1
                group = safeGroup
            elif message == "на эту неделю" and last_message == "":
                if group == "":
                    vk_session.method('messages.send',
                                      {'user_id': id, 'message': "Вы не уточнили группу!", 'random_id': 0})
                else:
                    for i in range(6):
                        if i != 0:
                            month = thisWeek.strftime("%B").lower()
                            month = changeMonth(month)
                            table = table + "\n" + "Расписание на " + nameDays[i] + " " + thisWeek.strftime(
                                "%d") + " " + month + "\n"
                        groupTimetable(thisWeek.strftime("%a").lower())
                        if group == "":
                            break
                        if i == 0:
                            month = thisWeek.strftime("%B").lower()
                            month = changeMonth(month)
                            table = "Расписание на " + nameDays[i] + " " + thisWeek.strftime(
                                "%d") + " " + month + "\n" + table
                        table += '\n'
                        thisWeek += datetime.timedelta(days=1)
                    if group == "":
                        vk_session.method('messages.send',
                                          {'user_id': id,
                                           'message': "В расписании нет такой группы! Попробуйте ввести другую группу.",
                                           'random_id': 0})
                    else:
                        vk_session.method('messages.send', {'user_id': id, 'message': table, 'random_id': 0})
                        table = ""
                        thisWeek = datetime.date.today() - datetime.timedelta(days=datetime.date.today().weekday())
                group = safeGroup
            elif message == "на следующую неделю" and last_message == "":
                if group == "":
                    vk_session.method('messages.send',
                                      {'user_id': id, 'message': "Вы не уточнили группу!", 'random_id': 0})
                else:
                    weekStudy += 1
                    for i in range(6):
                        if i != 0:
                            month = nextWeek.strftime("%B").lower()
                            month = changeMonth(month)
                            table = table + "\n" + "Расписание на " + nameDays[i] + " " + nextWeek.strftime(
                                "%d") + " " + month + "\n"
                        groupTimetable(nextWeek.strftime("%a").lower())
                        if group == "":
                            break
                        if i == 0:
                            month = nextWeek.strftime("%B").lower()
                            month = changeMonth(month)
                            table = "Расписание на " + nameDays[i] + " " + nextWeek.strftime(
                                "%d") + " " + month + "\n" + table
                        table += '\n'
                        nextWeek += datetime.timedelta(days=1)
                    if group == "":
                        vk_session.method('messages.send',
                                          {'user_id': id,
                                           'message': "В расписании нет такой группы! Попробуйте ввести другую группу.",
                                           'random_id': 0})
                    else:
                        vk_session.method('messages.send', {'user_id': id, 'message': table, 'random_id': 0})
                        table = ""
                        nextWeek = (datetime.date.today() + datetime.timedelta(weeks=1) - datetime.timedelta(
                            days=datetime.date.today().weekday()))
                    weekStudy -= 1
                group = safeGroup
            elif "бот" in message and message[4:] in nameDays:
                last_message = ""
                if group == "":
                    vk_session.method('messages.send',
                                      {'user_id': id, 'message': "Вы не уточнили группу!", 'random_id': 0})
                elif message[4:] == "воскресенье":
                    vk_session.method('messages.send',
                                      {'user_id': id, 'message': "По воскресеньям не учимся :)",
                                       'random_id': 0})
                    vk_session.method('messages.send',
                                      {'user_id': id, 'sticker_id': 8802, 'random_id': 0})
                else:
                    listDayWeek = [datetime.date(2022, 2, 21),
                                   datetime.date(2022, 2, 22),
                                   datetime.date(2022, 2, 23),
                                   datetime.date(2022, 2, 24),
                                   datetime.date(2022, 2, 25),
                                   datetime.date(2022, 2, 26)]
                    idx = 0
                    while message[4:] != nameDays[idx]:
                        idx += 1
                    groupTimetable(listDayWeek[idx].strftime("%a").lower())
                    if group == "":
                        vk_session.method('messages.send',
                                          {'user_id': id,
                                           'message': "В расписании нет такой группы! Попробуйте ввести другую группу.",
                                           'random_id': 0})
                    else:
                        weekStudy = 1
                        if message[4:] in ["понедельник", "вторник", "четверг"]:
                            table = "Расписание на нечетный " + message[4:] + "\n" + table + "\n"
                            table += "\nРасписание на четный " + message[4:] + "\n"
                        else:
                            table = "Расписание на нечетную " + message[4:-1] + "у\n" + table + "\n"
                            table += "\nРасписание на четную " + message[4:-1] + "у\n"
                        weekStudy = 0
                        groupTimetable((listDayWeek[idx] + datetime.timedelta(weeks=1)).strftime("%a").lower())
                        vk_session.method('messages.send', {'user_id': id, 'message': table, 'random_id': 0})
                        table = ""
                        weekStudy = int(datetime.date.today().strftime("%V")) - int(
                            datetime.date(2022, 2, 9).strftime("%V")) + 1
            elif "бот" in message and message[message.find(" ") + 1:message.rfind(" ")] in nameDays and re.search(
                    r'[а-яА-Я]{4}-\d{2}-\d{2}', message) is not None:
                last_message = ""
                group = message[message.rfind(" ") + 1:].upper()
                course = setCourse(group)
                sheet = allSheet[course-1]
                if message[message.find(" ") + 1:message.rfind(" ")] == "воскресенье":
                    vk_session.method('messages.send',
                                      {'user_id': id, 'message': "По воскресеньям не учимся :)",
                                       'random_id': 0})
                    vk_session.method('messages.send',
                                      {'user_id': id, 'sticker_id': 8802, 'random_id': 0})
                else:
                    listDayWeek = [datetime.date(2022, 2, 21),
                                   datetime.date(2022, 2, 22),
                                   datetime.date(2022, 2, 23),
                                   datetime.date(2022, 2, 24),
                                   datetime.date(2022, 2, 25),
                                   datetime.date(2022, 2, 26)]
                    idx = 0
                    while message[message.find(" ") + 1:message.rfind(" ")] != nameDays[idx]:
                        idx += 1
                    groupTimetable(listDayWeek[idx].strftime("%a").lower())
                    if group == "":
                        vk_session.method('messages.send',
                                          {'user_id': id,
                                           'message': "В расписании нет такой группы!",
                                           'random_id': 0})
                    else:
                        weekStudy = 1
                        if message[message.find(" ") + 1:message.rfind(" ")] in ["понедельник", "вторник", "четверг"]:
                            table = "Расписание на нечетный " + message[message.find(" "):message.rfind(
                                " ")] + "\n" + table + "\n"
                            table += "\nРасписание на четный " + message[message.find(" "):message.rfind(" ")] + "\n"
                        else:
                            table = "Расписание на нечетную " + message[message.find(" "):message.rfind(
                                " ") - 1] + "у\n" + table + "\n"
                            table += "\nРасписание на четную " + message[
                                                                 message.find(" "):message.rfind(" ") - 1] + "у\n"
                        weekStudy = 0
                        groupTimetable((listDayWeek[idx] + datetime.timedelta(weeks=1)).strftime("%a").lower())
                        vk_session.method('messages.send', {'user_id': id, 'message': table, 'random_id': 0})
                        table = ""
                        group = safeGroup
                        weekStudy = int(datetime.date.today().strftime("%V")) - int(
                            datetime.date(2022, 2, 9).strftime("%V")) + 1
            elif "бот" in message and re.search(r'[а-яА-Я]{4}-\d{2}-\d{2}', message) is not None and len(message) == 14:
                last_message = ""
                group = message[message.find(" ") + 1:].upper()
                course = setCourse(group)
                sheet = allSheet[course - 1]
                vk_session.method('messages.send', {'user_id': id, 'message': "Показать расписание группы " + group,
                                                    'keyboard': keyboard.get_keyboard(), 'random_id': 0})
            elif message == "погода":
                last_message = ""
                vk_session.method('messages.send', {'user_id': id, 'message': "Показать погоду в Москве",
                                                    'keyboard': weatherKeyboard.get_keyboard(), 'random_id': 0})
            elif message == "сейчас":
                last_message = ""
                weather_api = requests.get(
                    "http://api.openweathermap.org/data/2.5/weather?q=moscow&appid=cedff4064e83e3f289965131db177a37&units=metric&lang=ru")
                weather = weather_api.json()
                image = requests.get(
                    "http://openweathermap.org/img/wn/" + weather['weather'][0]['icon'] + "@2x.png",
                    stream=True)
                attachments = []
                photo = upload.photo_messages(photos=image.raw)[0]
                attachments.append("photo{}_{}".format(photo["owner_id"], photo["id"]))
                info_weather = str.capitalize(weather['weather'][0]['description']) + ", температура: " + str(
                    round(int(weather['main']['temp_min']))) + " - " + str(
                    round(int(weather['main']['temp_max']))) + " °C\nДавление: " + \
                               str(round(int(weather['main']['pressure']) / 1.33322)) + " мм рт.ст., влажность: " + str(
                    weather['main'][
                        'humidity']) + "%\nВетер: " + typeWind(float(weather['wind']['speed'])) + ", " + \
                               str(weather['wind'][
                                       'speed']) + " м/c, " + wayWind(float(weather['wind']['deg']))
                vk.messages.send(
                    message="Погода в Москве:\n",
                    random_id=0,
                    peer_id=id,
                    attachment=','.join(attachments)
                )
                vk_session.method('messages.send', {'user_id': id, 'message': info_weather, 'random_id': 0})
            elif message == "завтра" or message == "сегодня":
                last_message = ""
                weather_api = requests.get(
                    "http://api.openweathermap.org/data/2.5/forecast?lat=55.7522&lon=37.6156&appid=cedff4064e83e3f289965131db177a37&units=metric&lang=ru")
                weather = weather_api.json()
                info_weather = ""
                four_kind_day = ["УТРО", "ДЕНЬ", "ВЕЧЕР", "НОЧЬ"]
                time_moments = ["06:00:00", "12:00:00", "18:00:00", "00:00:00"]
                temp = "|| "
                num_pictures = 0
                for i in range(len(weather["list"])):
                    if (message == "завтра" and weather["list"][i]["dt_txt"] == (
                            datetime.date.today() + datetime.timedelta(days=1)).strftime("%Y-%m-%d") + " 06:00:00") or (
                            message == "сегодня" and weather["list"][i]["dt_txt"][
                                                     :10] == datetime.date.today().strftime("%Y-%m-%d") and int(
                        weather["list"][i]["dt_txt"][11:13]) % 6 == 0 and int(
                        weather["list"][i]["dt_txt"][11:13]) != 0) or (
                            message == "сегодня" and weather["list"][i]["dt_txt"] == (
                            datetime.date.today() + datetime.timedelta(days=1)).strftime("%Y-%m-%d") + " 00:00:00"):
                        for k in range(4):
                            if weather["list"][i]["dt_txt"][11:] != time_moments[k]:
                                continue
                            if message == "сегодня" and weather["list"][i]["dt_txt"][:10] == (
                                    datetime.date.today() + datetime.timedelta(days=1)).strftime("%Y-%m-%d") and \
                                    weather["list"][i]["dt_txt"][11:] != "00:00:00":
                                break
                            info_weather += four_kind_day[k] + "\n" + str.capitalize(
                                weather["list"][i]['weather'][0]['description']) + ", температура: " + str(
                                math.floor(float(weather["list"][i]['main']['temp_min']))) + " - " + str(
                                math.ceil(float(weather["list"][i]['main']['temp_max']))) + " °C\nДавление: " + \
                                            str(round(int(
                                                weather["list"][i]['main'][
                                                    'pressure']) / 1.33322)) + " мм рт.ст., влажность: " + str(
                                weather["list"][i]['main'][
                                    'humidity']) + "%\nВетер: " + typeWind(
                                float(weather["list"][i]['wind']['speed'])) + ", " + \
                                            str(weather["list"][i]['wind'][
                                                    'speed']) + " м/c, " + wayWind(
                                float(weather["list"][i]['wind']['deg']))
                            info_weather += "\n\n"
                            temp += str(round(float(weather["list"][i]['main']['temp']))) + "°C || "
                            image = requests.get(
                                "http://openweathermap.org/img/wn/" + weather["list"][i]['weather'][0][
                                    'icon'] + "@2x.png", stream=True)
                            if message == "сегодня":
                                with open("file" + str(k + 1) + "+.png", "wb") as f:
                                    f.write(image.content)
                                num_pictures += 1
                            else:
                                with open("file" + str(k + 1) + ".png", "wb") as f:
                                    f.write(image.content)
                            i += 2
                        break
                if message == "сегодня":
                    img = Image.new('RGBA', ((int(str(num_pictures) + "00")), 100))
                else:
                    img = Image.new('RGBA', (400, 100))
                if message == "сегодня":
                    h = -1
                    for t in range(4):
                        nameFile = "file" + str(t + 1) + "+.png"
                        if not Path(nameFile).is_file():
                            continue
                        h += 1
                        imgN = Image.open(nameFile)
                        img.paste(imgN, (0 + 100 * h, 0), imgN)
                else:
                    for t in range(4):
                        nameFile = "file" + str(t + 1) + ".png"
                        imgN = Image.open(nameFile)
                        img.paste(imgN, (0 + 100 * t, 0), imgN)
                if message == "завтра":
                    img = img.resize((180, 40), Resampling.LANCZOS)
                else:
                    if num_pictures == 1:
                        img = img.resize((50, 50), Resampling.LANCZOS)
                    elif num_pictures == 2:
                        img = img.resize((80, 40), Resampling.LANCZOS)
                    elif num_pictures == 3:
                        img = img.resize((130, 40), Resampling.LANCZOS)
                    else:
                        img = img.resize((180, 40), Resampling.LANCZOS)
                img.save("image.png")
                attachments = []
                photo = upload.photo_messages(photos="image.png")[0]
                attachments.append("photo{}_{}".format(photo["owner_id"], photo["id"]))
                if message == "завтра":
                    vk.messages.send(
                        message="Погода в Москве завтра:\n",
                        random_id=0,
                        peer_id=id,
                        attachment=','.join(attachments)
                    )
                else:
                    vk.messages.send(
                        message="Погода в Москве сегодня:\n",
                        random_id=0,
                        peer_id=id,
                        attachment=','.join(attachments)
                    )
                vk_session.method('messages.send', {'peer_id': id, 'message': temp, 'random_id': 0})
                vk_session.method('messages.send', {'peer_id': id, 'message': info_weather, 'random_id': 0})
            elif message == "на 5 дней":
                last_message = ""
                weather_api = requests.get(
                    "http://api.openweathermap.org/data/2.5/forecast?lat=55.7522&lon=37.6156&appid=cedff4064e83e3f289965131db177a37&units=metric&lang=ru")
                weather = weather_api.json()
                day_weather = "| "
                night_weather = "| "
                img = Image.new('RGBA', (500, 100))
                t = 0
                m = 0
                flag = False
                for i in range(len(weather["list"])):
                    if weather["list"][i]["dt_txt"][:10] == datetime.date.today().strftime("%Y-%m-%d") and int(
                            weather["list"][i]["dt_txt"][11:13]) > 15 and t < 5 and not flag:
                        flag = True
                        day_weather += "✖" + " | "
                        t += 1
                    elif weather["list"][i]["dt_txt"][11:] == "15:00:00" and t < 5:
                        flag = True
                        temp_day = str(round(weather["list"][i]["main"]["temp"])) if len(
                            str(round(weather["list"][i]["main"]["temp"]))) == 2 else "+" + str(
                            round(weather["list"][i]["main"]["temp"]))
                        day_weather += temp_day + "°C | "
                        t += 1
                        image = requests.get(
                            "http://openweathermap.org/img/wn/" + weather["list"][i]['weather'][0]['icon'] + "@2x.png",
                            stream=True)
                        with open("file" + str(t) + "5.png", "wb") as f:
                            f.write(image.content)
                    elif weather["list"][i]["dt_txt"][11:] == "00:00:00" and weather["list"][i]["dt_txt"][
                                                                             :10] != datetime.date.today().strftime(
                        "%Y-%m-%d"):
                        temp_night = str(round(weather["list"][i]["main"]["temp"])) if len(
                            str(round(weather["list"][i]["main"]["temp"]))) == 2 else "+" + str(
                            round(weather["list"][i]["main"]["temp"]))
                        night_weather += temp_night + "°C | "
                        m += 1
                if m == 4:
                    night_weather += "✖ | "
                for u in range(5):
                    nameFile = "file" + str(u + 1) + "5.png"
                    if not Path(nameFile).is_file():
                        continue
                    imgN = Image.open(nameFile)
                    img.paste(imgN, (0 + 100 * u, 0), imgN)
                img = img.resize((200, 40), Resampling.LANCZOS)
                img.save("image.png")
                attachments = []
                photo = upload.photo_messages(photos="image.png")[0]
                attachments.append("photo{}_{}".format(photo["owner_id"], photo["id"]))
                vk.messages.send(
                    message="Погода в Москве с " + datetime.date.today().strftime(
                        "%d.%m") + "-" + (datetime.date.today() + datetime.timedelta(days=4)).strftime("%d.%m"),
                    random_id=0,
                    peer_id=id,
                    attachment=','.join(attachments)
                )
                vk_session.method('messages.send', {'peer_id': id, 'message': day_weather + "ДЕНЬ", 'random_id': 0})
                vk_session.method('messages.send', {'peer_id': id, 'message': night_weather + "НОЧЬ", 'random_id': 0})
            elif "найти" in message and len(message) > 6:
                last_message = ""
                teacher = str.capitalize(message[6:])
                same_teachers = searchTeacher(teacher)
                if len(same_teachers) == 0:
                    vk_session.method('messages.send',
                                      {'peer_id': id, 'message': "Такого преподавателя нет!", 'random_id': 0})
                    teacher = ""
                elif len(same_teachers) == 1:
                    teacher = same_teachers[0]
                    vk_session.method('messages.send',
                                      {'user_id': id, 'message': "Показать расписание преподавателя " + teacher,
                                       'keyboard': keyboard1.get_keyboard(), 'random_id': 0})
                    last_message = "Показать расписание преподавателя"
                else:
                    nameKeyboard = VkKeyboard(one_time=True)
                    for name in range(len(same_teachers)):
                        nameKeyboard.add_button(label=same_teachers[name], color=VkKeyboardColor.PRIMARY)
                        if name != len(same_teachers) - 1:
                            nameKeyboard.add_line()
                    vk_session.method('messages.send', {'user_id': id, 'message': "Выберите преподавателя",
                                                        'keyboard': nameKeyboard.get_keyboard(), 'random_id': 0})
                    last_message = "Выберите преподавателя"
            elif last_message == "Выберите преподавателя":
                teacher = add_message
                vk_session.method('messages.send',
                                  {'user_id': id, 'message': "Показать расписание преподавателя " + teacher,
                                   'keyboard': keyboard1.get_keyboard(), 'random_id': 0})
                last_message = "Показать расписание преподавателя"
            elif last_message == "Показать расписание преподавателя" and message == "на сегодня":
                if today == "вс":
                    vk_session.method('messages.send',
                                      {'user_id': id, 'message': "Выходной :)",
                                       'random_id': 0})
                    vk_session.method('messages.send',
                                      {'user_id': id, 'sticker_id': 8797, 'random_id': 0})
                else:
                    ras = teacherTimetable(teacher)
                    month = datetime.date.today().strftime("%B").lower()
                    month = changeMonth(month)
                    d = datetime.date.today()
                    teacher_table += "Расписание преподавателя " + teacher + " " + d.strftime('%d ') + month + '\n'
                    for k in range(6):
                        teacher_table += str(k + 1) + ") " + \
                                         ras[(numWeek(d) + 1) % 2][weekday[int(d.isoweekday())]][k] + '\n'
                    vk_session.method('messages.send', {'user_id': id, 'message': teacher_table, 'random_id': 0})
                teacher_table = ""
                last_message = ""
            elif last_message == "Показать расписание преподавателя" and message == "на завтра":
                if tomorrow == "вс":
                    vk_session.method('messages.send',
                                      {'user_id': id, 'message': "Выходной :)",
                                       'random_id': 0})
                    vk_session.method('messages.send',
                                      {'user_id': id, 'sticker_id': 8797, 'random_id': 0})
                else:
                    ras = teacherTimetable(teacher)
                    month = (datetime.date.today() + datetime.timedelta(days=1)).strftime("%B").lower()
                    month = changeMonth(month)
                    d = datetime.date.today() + datetime.timedelta(days=1)
                    teacher_table += "Расписание преподавателя " + teacher + " " + d.strftime('%d ') + month + '\n'
                    for k in range(6):
                        teacher_table += str(k + 1) + ") " + ras[(numWeek(d) + 1) % 2][weekday[int(d.isoweekday())]][
                            k] + '\n'
                    vk_session.method('messages.send', {'user_id': id, 'message': teacher_table, 'random_id': 0})
                teacher_table = ""
                last_message = ""
            elif last_message == "Показать расписание преподавателя" and message == "на эту неделю":
                ras = teacherTimetable(teacher)
                teacher_table += "Расписание на эту неделю для преподавателя " + teacher + '\n'
                d = datetime.date.today()
                month = thisWeek.strftime("%B").lower()
                month = changeMonth(month)
                for i in range(1, 7):
                    teacher_table += "\n" + "Расписание на " + weekday[i] + " " + (
                            thisWeek + datetime.timedelta(days=i - 1)).strftime("%d") + " " + month + "\n"
                    for j in range(6):
                        teacher_table += str(j + 1) + ") " + ras[(numWeek(d) + 1) % 2][weekday[i]][j] + '\n'
                vk_session.method('messages.send', {'user_id': id, 'message': teacher_table, 'random_id': 0})
                teacher_table = ""
                last_message = ""
            elif last_message == "Показать расписание преподавателя" and message == "на следующую неделю":
                ras = teacherTimetable(teacher)
                teacher_table += "Расписание на следующую неделю для преподавателя " + teacher + '\n'
                d = datetime.date.today() + datetime.timedelta(weeks=1)
                month = nextWeek.strftime("%B").lower()
                month = changeMonth(month)
                for i in range(1, 7):
                    teacher_table += "\n" + "Расписание на " + weekday[i] + " " + (
                            nextWeek + datetime.timedelta(days=i - 1)).strftime("%d") + " " + month + "\n"
                    for j in range(6):
                        teacher_table += str(j + 1) + ") " + ras[(numWeek(d) + 1) % 2][weekday[i]][j] + '\n'
                vk_session.method('messages.send', {'user_id': id, 'message': teacher_table, 'random_id': 0})
                teacher_table = ""
                last_message = ""
            elif message == "корона":
                answer_site = True
                try:
                    corona_site = requests.get("https://coronavirusstat.ru/country/russia/")
                    corona_soup = BeautifulSoup(corona_site.text, "html.parser")
                    list_corona = corona_soup.findAll('div', {'class': 'col-12 p-0'})
                    for i in list_corona:
                        reg = i.find('a').text
                        site = i.find('a').get('href')
                        region_corona[reg] = site
                except Exception:
                    answer_site = False
                if answer_site:
                    corona_date = corona_soup.find('div', {'class': 'border rounded mt-3 mb-3 p-3'}).find('h6', {
                        'class': 'text-muted'}).text[:-17]
                    corona_result = corona_date + "\nСлучаев: " + corona_soup.find('div',
                                                                                   {'title': 'Короновирус Россия: Случаев'}).text + " (" + corona_soup.find(
                        'span', {
                            'class': 'font-weight-bold text-text-dark'}).text + " за сегодня)\n" + "Активных: " + corona_soup.find(
                        'div', {'title': 'Короновирус Россия: Активных'}).text + " (" + corona_soup.find('span', {
                        'class': 'font-weight-bold text-primary'}).text + " за сегодня)\n" + "Вылечено: " + corona_soup.find(
                        'div',
                        {'title': 'Короновирус Россия: Вылечено'}).text + " (" + corona_soup.find(
                        'span', {
                            'class': 'font-weight-bold text-success'}).text + " за сегодня)\n" + "Умерло: " + corona_soup.find(
                        'div', {'title': 'Короновирус Россия: Умерло'}).text + " (" + corona_soup.find('span', {
                        'class': 'font-weight-bold text-danger'}).text + " за сегодня)"
                    vk_session.method('messages.send', {'peer_id': id, 'message': corona_result, 'random_id': 0})
                else:
                    vk_session.method('messages.send',
                                      {'peer_id': id, 'message': "Не получается сделать запрос на сайт...", 'random_id': 0})
                    vk_session.method('messages.send', {'peer_id': id, 'sticker_id': 11748, 'random_id': 0})
            elif "корона" in message and len(message) > 7:
                answer_site = True
                try:
                    corona_site = requests.get("https://coronavirusstat.ru/country/russia/")
                    corona_soup = BeautifulSoup(corona_site.text, "html.parser")
                    list_corona = corona_soup.findAll('div', {'class': 'col-12 p-0'})
                    for i in list_corona:
                        reg = i.find('a').text
                        site = i.find('a').get('href')
                        region_corona[reg] = site
                except Exception:
                    answer_site = False
                if answer_site:
                    user_reg = message[message.find(" ") + 1:]
                    user_site = ''
                    for r in region_corona:
                        if user_reg.lower() in r.lower():
                            user_reg = r
                            user_site = region_corona.get(r)
                            break
                    if user_site == '':
                        vk_session.method('messages.send', {'peer_id': id, 'message': "Регион не найден!", 'random_id': 0})
                    else:
                        reg_site = requests.get("https://coronavirusstat.ru" + user_site)
                        reg_soup = BeautifulSoup(reg_site.text, "html.parser")
                        reg_date = reg_soup.find('div', {'class': 'border rounded mt-3 mb-3 p-3'}).find('h6', {
                            'class': 'text-muted'}).text[:-17]
                        reg_name = "Короновирус " + reg_soup.find('div', {'class': 'border rounded mt-3 mb-3 p-3'}).find(
                            'h1',
                            {'class': 'h2 font-weight-bold'}).text[12:]
                        reg_result = reg_date + "\nРегион: " + user_reg + "\nСлучаев: " + reg_soup.find('div', {
                            'title': reg_name + ": Случаев"}).text + " (" + reg_soup.find(
                            'span', {
                                'class': 'font-weight-bold text-text-dark'}).text + " за сегодня)\n" + "Активных: " + reg_soup.find(
                            'div', {'title': reg_name + ": Активных"}).text + " (" + reg_soup.find('span', {
                            'class': 'font-weight-bold text-primary'}).text + " за сегодня)\n" + "Вылечено: " + reg_soup.find(
                            'div', {'title': reg_name + ": Вылечено"}).text + " (" + reg_soup.find(
                            'span', {
                                'class': 'font-weight-bold text-success'}).text + " за сегодня)\n" + "Умерло: " + reg_soup.find(
                            'div', {'title': reg_name + ": Умерло"}).text + " (" + reg_soup.find('span', {
                            'class': 'font-weight-bold text-danger'}).text + " за сегодня)"

                        vk_session.method('messages.send', {'peer_id': id, 'message': reg_result, 'random_id': 0})
                else:
                    vk_session.method('messages.send',
                                      {'peer_id': id, 'message': "Не получается сделать запрос на сайт...",
                                       'random_id': 0})
                    vk_session.method('messages.send', {'peer_id': id, 'sticker_id': 11748, 'random_id': 0})
            else:
                vk_session.method('messages.send', {'peer_id': id, 'sticker_id': 13897, 'random_id': 0})
