from collections import Counter
from time import sleep

import requests
from bs4 import BeautifulSoup

NUMBER_TEAM = "2292"  # Введите ваш номер команды (2292) (21310)
SEASON = "69"  # Введите сезон (68)
TOURNAMENT_TYPES = {
    "Товарищеский": "1",
    "Кубок межсезонья": "2",
    "Чемпионат": "3",
    "Кубок страны": "4",
    "Комм. турнир": "5",
    "Лига чемпионов": "8",
    "Лига Европы": "14",
    "Нац. суперкубок": "34",
    "Кубок вызова": "47",
}
COLOR_TEXT_TYPES = {
    "зеленый": "color:#00FF00",
    "красный": "color:#FF0000",
}
ATTACKING_PLAYERS = ["CF", "ST", "RF", "LF", "RW", "LW", "AM"]


def process_game_place(index, num_range, gif_id_prefix):
    for num in num_range:
        mini_result.append(tds[num].find("i").text)
    mini_result.append(auto_delivery_list[index])
    positions = "-".join(
        [soup.find("div", id=f"{gif_id_prefix}_{i}").text for i in range(11)]
    )
    mini_result.append(positions)
    return positions


url_my_team = f"https://www.virtualsoccer.ru/roster.php?num={NUMBER_TEAM}"
response = requests.get(url_my_team).text
soup = BeautifulSoup(response, "lxml")
divs = soup.find_all("div", class_="lh14 txt2r")

for div in divs:
    if div.find("a", class_="mnu qt"):
        for tournament_type in TOURNAMENT_TYPES:
            if tournament_type in div.text:
                filter_tournament = TOURNAMENT_TYPES[tournament_type]
                break
        # Извлекаем имя команды ближайшего соперника в ближайшем турнире
        name_team = div.find("a").text
        href_team = div.find("a").get("href")
        # Извлекаем номер команды ближайшего соперника в ближайшем турнире
        num_team = href_team.replace("roster.php?num=", "")
        break

# Переходим по ссылке команды ближайшего соперника (все матчи)
sleep(1)
response = requests.get(
    f"https://www.virtualsoccer.ru/roster_m.php?season={SEASON}&num={num_team}&season={SEASON}&filter={filter_tournament}"
).text

soup = BeautifulSoup(response, "lxml")
trs = soup.find_all("tr", bgcolor="#EEEEEE")

# Собираем ссылки всех сыгранных матчей соперника + Д/Г + автосостав
matchs_list = []
games_place = []
auto_delivery_list = []

for tr in trs:
    href_match = tr.find("a", class_="hl").get("href")
    matchs_list.append(href_match)

    place = tr.find("td", class_="lh16 txt qt").get("title")
    games_place.append(place)

    auto_delivery = tr.find("td", title="Автосостав")
    if auto_delivery:
        auto_delivery_list.append("*")
    else:
        auto_delivery_list.append("")


# Проходимся по ссылкам всех матчей соперника и извлекаем нужную инфу
result = []
for index in range(len(games_place)):
    url = "https://www.virtualsoccer.ru/" + matchs_list[index]
    sleep(1)
    response = requests.get(url).text
    soup = BeautifulSoup(response, "lxml")
    tds = soup.find_all("td", class_="lh18 txt")

    mini_result = []

    if games_place[index] == "Дома":
        positions = process_game_place(index, [0, 2, 4, 6], "gif_0")
    elif games_place[index] == "В гостях":
        positions = process_game_place(index, [1, 3, 5, 7], "gif_1")

    attacking_players_count = 0
    for player in ATTACKING_PLAYERS:
        count = positions.count(player)
        attacking_players_count += count
    attacking_players = str(attacking_players_count) + " игр. атаки"
    mini_result.append(attacking_players)

    if "style" in tds[4].attrs:
        if tds[4]["style"] == COLOR_TEXT_TYPES["зеленый"]:
            mini_result.append(True)
        elif tds[4]["style"] == COLOR_TEXT_TYPES["красный"]:
            mini_result.append(False)
    else:
        mini_result.append(None)

    result.append(mini_result)

style_collisions = Counter(match[2] for match in result)
number_attack_players = Counter(match[6] for match in result)
type_protection = Counter(match[3] for match in result)
auto_delivery = Counter(match[4] for match in result)

print()
print(f"Ваш ближайший турнир - {tournament_type}")
print(f"Ваш ближайший соперник - {name_team}")
for match in result:
    print(match)
print()
print(style_collisions)
print(type_protection)
print(auto_delivery)
print(number_attack_players)
print()
