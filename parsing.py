from time import sleep

import requests
from bs4 import BeautifulSoup

number_team = "2292"  # Введите ваш номер команды
season = "69"
filter = "3"  # 3 - чемпионат

# Извлекаем номер и имя команды ближайшего соперника
url_my_team = f"https://www.virtualsoccer.ru/roster.php?num={number_team}"
response = requests.get(url_my_team).text
soup = BeautifulSoup(response, "lxml")
divs = soup.find_all("div", class_="lh14 txt2r")

for div in divs:
    if div.find("a", class_="mnu qt"):
        name_team = div.find("a").text
        href_team = div.find("a").get("href")
        num_team = href_team.replace("roster.php?num=", "")
        break

# Переходим по ссылке команды ближайшего соперника (все матчи)
sleep(1)
response = requests.get(
    f"https://www.virtualsoccer.ru/roster_m.php?season={season}&num={num_team}&season={season}&filter={filter}"
).text

soup = BeautifulSoup(response, "lxml")
trs = soup.find_all("tr", bgcolor="#EEEEEE")

# Собираем ссылки всех сыгранных матчей соперника + Д/Г
matchs_list = []
games_place = []
for tr in trs:
    href_match = tr.find("a", class_="hl").get("href")
    matchs_list.append(href_match)
    place = tr.find("td", class_="lh16 txt qt").get("title")
    games_place.append(place)

# Проходимся по ссылкам всех матчей соперника и извлекаем нужную инфу
result = []
for index in range(len(games_place)):
    # for index in range(1):
    url = "https://www.virtualsoccer.ru/" + matchs_list[index]
    sleep(1)
    response = requests.get(url).text
    soup = BeautifulSoup(response, "lxml")
    tds = soup.find_all("td", class_="lh18 txt")

    mini_result = []

    if games_place[index] == "Дома":
        mini_result.append(tds[0].find("i").text)
        mini_result.append(tds[2].find("i").text)
        mini_result.append(tds[4].find("i").text)
        mini_result.append(tds[6].find("i").text)
    else:
        mini_result.append(tds[1].find("i").text)
        mini_result.append(tds[3].find("i").text)
        mini_result.append(tds[5].find("i").text)
        mini_result.append(tds[7].find("i").text)
    result.append(mini_result)
print(result)
