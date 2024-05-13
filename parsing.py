from collections import Counter
from time import sleep

import requests
from bs4 import BeautifulSoup

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


def process_game_place(
    index,
    num_range,
    gif_id_prefix,
    tds,
    auto_delivery_list,
    power_ratings,
    mini_result,
    soup,
):
    for num in num_range:
        mini_result.append(tds[num].find("i").text)
    mini_result.append(auto_delivery_list[index])
    mini_result.append(power_ratings[index])
    positions = "-".join(
        [soup.find("div", id=f"{gif_id_prefix}_{i}").text for i in range(11)]
    )
    mini_result.append(positions)
    return positions


def main(your_team_number, season):
    """
    Основная функция программы.

    Args:
        your_team_number (int): Номер твоей команды.
        season (int): Номер сезона.

    Returns:
        opponent_team_number(int): Номер команды ближайшего соперника в ближайшем турнире.
    """
    url_my_team = (
        f"https://www.virtualsoccer.ru/roster.php?num={your_team_number}"
    )
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
            opponent_team_number = href_team.replace("roster.php?num=", "")
            break

    # Переходим по ссылке команды ближайшего соперника (все матчи)
    sleep(1)
    response = requests.get(
        f"https://www.virtualsoccer.ru/roster_m.php?season={season}&num={opponent_team_number}&season={season}&filter={filter_tournament}"
    ).text

    soup = BeautifulSoup(response, "lxml")
    trs = soup.find_all("tr", bgcolor="#EEEEEE")

    # Собираем ссылки всех сыгранных матчей соперника + Д/Г + автосостав + рэйтинг
    matchs_list = []
    games_place = []
    auto_delivery_list = []
    power_ratings = []

    for tr in trs:
        href_match = tr.find("a", class_="hl").get("href")
        matchs_list.append(href_match)

        place = tr.find("td", class_="lh16 txt qt").get("title")
        games_place.append(place)

        ratings = tr.find("td", class_="lh16 txt5r qh").text
        power_ratings.append(ratings)

        auto_delivery = tr.find("td", title="Автосостав")
        if auto_delivery:
            auto_delivery_list.append("*")
        else:
            auto_delivery_list.append("")

    # Находим рейтинг команды с которой предстоит играть ближайший матч
    last_bgcolor_tr_tag = soup.find_all("tr", {"bgcolor": "#EEEEEE"})[-1]
    next_tr_tag = last_bgcolor_tr_tag.find_next("tr")
    current_rating = next_tr_tag.find("td", class_="lh16 txt5r qh").text

    # Проходимся по ссылкам всех матчей соперника и извлекаем нужную инфу
    result = []
    result_cost = []
    for index in range(len(games_place)):
        url = "https://www.virtualsoccer.ru/" + matchs_list[index]
        sleep(1)
        response = requests.get(url).text
        soup = BeautifulSoup(response, "lxml")
        tds = soup.find_all("td", class_="lh18 txt")

        mini_result = []
        mini_result_cost = []

        if games_place[index] == "Дома":
            positions = process_game_place(
                index,
                [0, 2, 4, 6],
                "gif_0",
                tds,
                auto_delivery_list,
                power_ratings,
                mini_result,
                soup,
            )

            # Извлекаем вместимость стадиона,
            # количество зрителей на матче, цену билета.
            basic_match_information = soup.find(
                "div", style="padding:3px 0 1px 0"
            ).get_text()

            start_index = basic_match_information.find("(")
            end_index = basic_match_information.find(")", start_index)
            stadium_capacity = int(
                basic_match_information[start_index + 1 : end_index].replace(
                    " ", ""
                )
            )
            mini_result_cost.append(stadium_capacity)

            start_index = basic_match_information.find("Зрителей:") + len(
                "Зрителей:"
            )
            end_index = basic_match_information.find(".", start_index)
            number_of_viewers = int(
                basic_match_information[start_index:end_index].replace(" ", "")
            )
            mini_result_cost.append(number_of_viewers)

            start_index = basic_match_information.find("Билет:") + len(
                "Билет:"
            )
            ticket_price = int(basic_match_information[start_index:].strip())
            mini_result_cost.append(ticket_price)

            # Считаем доход от продажи билетов.
            income = number_of_viewers * ticket_price
            mini_result_cost.append(income)
            result_cost.append(mini_result_cost)

        elif games_place[index] == "В гостях":
            positions = process_game_place(
                index,
                [1, 3, 5, 7],
                "gif_1",
                tds,
                auto_delivery_list,
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

        if "style" in tds[4].attrs:
            if tds[4]["style"] == COLOR_TEXT_TYPES["зеленый"]:
                mini_result.append(True)
            elif tds[4]["style"] == COLOR_TEXT_TYPES["красный"]:
                mini_result.append(False)
        else:
            mini_result.append(None)

        mini_result.append(f"{index+1} тур")

        result.append(mini_result)

    style_collisions = Counter(match[2] for match in result)
    type_protection = Counter(match[3] for match in result)
    auto_delivery = Counter(match[4] for match in result)
    number_attack_players = Counter(match[7] for match in result)

    print()
    print(f"Турнир - {tournament_type}. Сезон - {season}.")
    print(f"Футбольная команда - {name_team.upper()}")
    print(f"Рейтинг силы ближайшего соперника - {current_rating}")
    print("Матчи:")

    # Сортируем матчи по рейтингам соперников
    sorted_result = sorted(result, key=lambda x: int(x[5][:-1]), reverse=True)
    for match in sorted_result:
        print(str(match))
    print()
    print("Статистика:")
    print(dict(style_collisions))
    print(dict(type_protection))
    print(dict(auto_delivery))
    print(dict(number_attack_players))
    print()
    print("Вместимость стадиона, Количество зрителей, Цена билета, Доход:")
    for result in result_cost:
        print(result)
    print()

    return opponent_team_number


if __name__ == "__main__":
    opponent_team_number = main(2292, 69)
    main(opponent_team_number, 69)

# 2292 21310 14378
