# Проверить как работает на товарищеских матчах. Д/Г
# 2292 21310 14378

import random
from collections import Counter
from time import sleep

import requests
from bs4 import BeautifulSoup

MY_TEAM_NUMBER = 21310
SEASON = 69
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

MATCH_STATISTICS_TEAM_PLAYED_HOME = [0, 2, 4, 6]
MATCH_STATISTICS_TEAM_PLAYED_AWAY = [1, 3, 5, 7]
SEARCH_STR_TEAM_PLAYED_HOME = "gif_0"
SEARCH_STR_TEAM_PLAYED_AWAY = "gif_1"


def get_next_opponents(your_team_number):
    """
    Получает информацию о ближайших соперниках.

    Args:
        your_team_number (int): Номер вашей команды.

    Returns:
        list: Список кортежей, каждый из которых содержит информацию о следующем сопернике.
              Каждый кортеж состоит из трех элементов:
              - Номер команды соперника (str)
              - Имя команды соперника (str)
              - Тип турнира (str)
    """
    next_opponents = []
    url_my_team = (
        f"https://www.virtualsoccer.ru/roster.php?num={your_team_number}"
    )
    response = requests.get(url_my_team).text
    soup = BeautifulSoup(response, "lxml")
    for previewmatch in soup.select("div.lh14.txt2r:has(a.mnu.qt)"):
        for tournament_type in TOURNAMENT_TYPES:
            if tournament_type in previewmatch.text:
                opponent_team_name = previewmatch.a.text
                opponent_team_number = previewmatch.a["href"].replace(
                    "roster.php?num=", ""
                )
                next_opponents.append(
                    (opponent_team_number, opponent_team_name, tournament_type)
                )
                break
    return next_opponents


def check_free_team(team_number):
    """Проверка свободна ли команда."""
    url_team = f"https://www.virtualsoccer.ru/roster.php?num={team_number}"
    response = requests.get(url_team).text
    soup = BeautifulSoup(response, "lxml")
    password_and_free_team = soup.find_all("img", class_="qt", title=True)
    if len(password_and_free_team) >= 2:
        title = password_and_free_team[1]["title"]
        return title
    return None


def find_manager_working(team_number):
    """С какого времени работает менеджер в команде."""
    url_team = f"https://www.virtualsoccer.ru/roster.php?num={team_number}"
    response = requests.get(url_team).text
    soup = BeautifulSoup(response, "lxml")
    team_basic_information = soup.find_all("div", class_="lh17 txtl")
    if not team_basic_information[0].find("a"):
        return None
    name_manager = team_basic_information[0].find("a").text
    nick_manager = team_basic_information[1].find("b").text

    for index in range(1, 20):
        sleep(random.uniform(0.1, 0.5))
        url_team_events_page = f"https://www.virtualsoccer.ru/roster_e.php?num={team_number}&page={index}"
        response = requests.get(url_team_events_page).text
        soup = BeautifulSoup(response, "lxml")
        events = soup.find_all("tr")[12:]
        for event in events:
            if (
                "принят на работу тренером-менеджером в команду"
                in event.find("td", class_="lh18 txtl").text
            ):
                season = (
                    event.find("td", class_="lh18 txt2 qtt")
                    .contents[-1]
                    .strip()
                )
                day = event.find("td", class_="lh18 txt2r qtt").text
                date = event.find_all("td", class_="lh18 txt2r qtt")[1].text
                return name_manager, nick_manager, season, day, date


def get_ticket_sales(soup, result_cost, mini_result_cost):

    basic_match_information = soup.find(
        "div", style="padding:3px 0 1px 0"
    ).get_text()

    start_index = basic_match_information.find("(")
    end_index = basic_match_information.find(")", start_index)
    stadium_capacity = int(
        basic_match_information[start_index + 1 : end_index].replace(" ", "")
    )
    mini_result_cost.append(stadium_capacity)

    start_index = basic_match_information.find("Зрителей:") + len("Зрителей:")
    end_index = basic_match_information.find(".", start_index)
    number_of_viewers = int(
        basic_match_information[start_index:end_index].replace(" ", "")
    )
    mini_result_cost.append(number_of_viewers)

    start_index = basic_match_information.find("Билет:") + len("Билет:")
    ticket_price = int(basic_match_information[start_index:].strip())
    mini_result_cost.append(ticket_price)

    # Считаем доход от продажи билетов.
    income = number_of_viewers * ticket_price
    mini_result_cost.append(income)
    result_cost.append(mini_result_cost)
    return result_cost


def process_game_place(
    index,
    match_statistics_team_played,
    search_str_team_played,
    match_statistics,
    auto_positions,
    power_ratings,
    mini_result,
    soup,
):
    for num in match_statistics_team_played:
        mini_result.append(match_statistics[num].find("i").text)
    mini_result.append(auto_positions[index])
    mini_result.append(power_ratings[index])
    positions = "-".join(
        [
            soup.find("div", id=f"{search_str_team_played}_{i}").text
            for i in range(11)
        ]
    )
    mini_result.append(positions)
    return positions


def main(season, opponent_team_number, tournament_type, flag_ticket):
    # Смотрим все сыгранные матчи соперника в определенном турнире и сезоне.
    filter_tournament = TOURNAMENT_TYPES[tournament_type]
    url_opponent_games = f"https://www.virtualsoccer.ru/roster_m.php?season={season}&num={opponent_team_number}&season={season}&filter={filter_tournament}"
    response = requests.get(url_opponent_games).text
    soup = BeautifulSoup(response, "lxml")
    matches_played = soup.find_all("tr", bgcolor="#EEEEEE")

    url_matches_played = []  # Ссылки на сыгранные матчи соперника.
    games_place = []  # "Дома" или "В гостях".
    auto_positions = []  # Автосостав ("*" или "").
    power_ratings = []  # Рейтинг силы соперника.

    for match_played in matches_played:
        href_match = match_played.find("a", class_="hl").get("href")
        url_matches_played.append(href_match)

        place = match_played.find("td", class_="lh16 txt qt").get("title")
        games_place.append(place)

        ratings = match_played.find("td", class_="lh16 txt5r qh").text
        power_ratings.append(ratings)

        auto_delivery = match_played.find("td", title="Автосостав")
        if auto_delivery:
            auto_positions.append("*")
        else:
            auto_positions.append("")

    # Находим рейтинг команды с которой предстоит играть ближайший матч.
    last_bgcolor_tr_tag = soup.find_all("tr", {"bgcolor": "#EEEEEE"})[-1]
    next_tr_tag = last_bgcolor_tr_tag.find_next("tr")
    current_rating_opponent = next_tr_tag.find(
        "td", class_="lh16 txt5r qh"
    ).text

    # Проходимся по ссылкам всех матчей соперника и извлекаем нужную инфу
    result = []
    result_cost = []
    for index in range(len(url_matches_played)):
        sleep(random.uniform(0.1, 0.5))
        url = "https://www.virtualsoccer.ru/" + url_matches_played[index]
        response = requests.get(url).text
        soup = BeautifulSoup(response, "lxml")
        match_statistics = soup.find_all("td", class_="lh18 txt")

        mini_result = []
        mini_result_cost = []

        if games_place[index] == "Дома":
            positions = process_game_place(
                index,
                MATCH_STATISTICS_TEAM_PLAYED_HOME,
                SEARCH_STR_TEAM_PLAYED_HOME,
                match_statistics,
                auto_positions,
                power_ratings,
                mini_result,
                soup,
            )

            if flag_ticket:
                result_cost = get_ticket_sales(
                    soup, result_cost, mini_result_cost
                )

        elif games_place[index] == "В гостях":
            positions = process_game_place(
                index,
                MATCH_STATISTICS_TEAM_PLAYED_AWAY,
                SEARCH_STR_TEAM_PLAYED_AWAY,
                match_statistics,
                auto_positions,
                power_ratings,
                mini_result,
                soup,
            )

        attacking_players_count = 0
        for player in ATTACKING_PLAYERS:
            count = positions.count(player)
            attacking_players_count += count
        attacking_players = str(attacking_players_count) + " игр. атаки"
        mini_result.append(attacking_players)

        if "style" in match_statistics[4].attrs:
            if match_statistics[4]["style"] == COLOR_TEXT_TYPES["зеленый"]:
                mini_result.append(True)
            elif match_statistics[4]["style"] == COLOR_TEXT_TYPES["красный"]:
                mini_result.append(False)
        else:
            mini_result.append(None)

        mini_result.append(f"{index+1} тур")

        result.append(mini_result)

    style_collisions = Counter(match[2] for match in result)
    type_protection = Counter(match[3] for match in result)
    auto_delivery = Counter(match[4] for match in result)
    # number_attack_players = Counter(match[7] for match in result)

    count_personally = 0
    count_zonal = 0
    for match in result:
        attacking_players = match[7]
        amount_attacking_players = int(attacking_players[0])
        if amount_attacking_players <= 3:
            count_personally += 1
        elif amount_attacking_players > 3:
            count_zonal += 1

    return (
        current_rating_opponent,
        style_collisions,
        type_protection,
        auto_delivery,
        count_personally,
        count_zonal,
        result,
        result_cost,
    )


if __name__ == "__main__":
    next_opponents = get_next_opponents(MY_TEAM_NUMBER)
    opponent_team_number = next_opponents[0][0]
    name_team = next_opponents[0][1]
    tournament_type = next_opponents[0][2]

    statistics = main(SEASON, opponent_team_number, tournament_type, False)
    current_rating_opponent = statistics[0]
    style_collisions = statistics[1]
    type_protection = statistics[2]
    auto_delivery = statistics[3]
    count_personally = statistics[4]
    count_zonal = statistics[5]
    result = statistics[6]

    team_manager = find_manager_working(opponent_team_number)
    if team_manager:
        name_manager = team_manager[0]
        nick_manager = team_manager[1]
        season = team_manager[2]
        day = team_manager[3]
        date = team_manager[4]

    print()
    print(f"Турнир - {tournament_type}. Сезон - {str(SEASON)}.")
    print(f"Футбольная команда - {name_team.upper()}")
    free_team = check_free_team(opponent_team_number)
    if free_team:
        print(free_team, "!")
    if team_manager:
        print(
            f"Менеджер '{name_manager}'. Ник '{nick_manager}'. Назначен {date}. Сезон {season}. Виртуальный игровой день {day}."
        )
    else:
        print("Менеджер отсутсвует !")
    print(f"Рейтинг силы ближайшего соперника - {current_rating_opponent}")
    print("Матчи, отсортированы по рейтингу соперников:")

    # Сортируем матчи по рейтингам соперников
    sorted_result = sorted(result, key=lambda x: int(x[5][:-1]), reverse=True)
    for match in sorted_result:
        print(str(match))
    print()
    print("СТАТИСТИКА:")
    print("Стиль:")
    print(dict(style_collisions))
    print("Вид защиты:")
    print(dict(type_protection))
    print("Автосоставы:")
    print(dict(auto_delivery))
    print("Игроки атаки:")
    print(f" - до 3 игроков атаки - {count_personally} раз.")
    print(f" - 4 и более игроков атаки - {count_zonal} раз.")

    next_opponents = get_next_opponents(opponent_team_number)
    opponent_team_number = next_opponents[0][0]
    name_team = next_opponents[0][1]
    tournament_type = next_opponents[0][2]

    statistics = main(SEASON, opponent_team_number, tournament_type, True)
    current_rating_opponent = statistics[0]
    style_collisions = statistics[1]
    type_protection = statistics[2]
    auto_delivery = statistics[3]
    count_personally = statistics[4]
    count_zonal = statistics[5]
    result = statistics[6]
    result_cost = statistics[7]

    print()
    print(f"Турнир - {tournament_type}. Сезон - {str(SEASON)}.")
    print(f"Футбольная команда - {name_team.upper()}")
    print(f"Рейтинг силы ближайшего соперника - {current_rating_opponent}")
    print("Матчи, отсортированы по турам:")

    for match in result:
        print(str(match))
    print()
    print("СТАТИСТИКА:")
    print("Стиль:")
    print(dict(style_collisions))
    print("Вид защиты:")
    print(dict(type_protection))
    print("Автосоставы:")
    print(dict(auto_delivery))
    print("Игроки атаки:")
    print(f" - до 3 игроков атаки - {count_personally} раз.")
    print(f" - 4 и более игроков атаки - {count_zonal} раз.")
    print()
    print("ПРОДАЖА БИЛЕТОВ:")
    print("Вместимость стадиона, Количество зрителей, Цена билета, Доход:")
    for result in result_cost:
        print(result)
    print()
