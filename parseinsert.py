"""Inserts the data from raw .json files into a SQLite db."""

import datetime
import json
import os
import sqlite3
from pathlib import Path

# Historical Trend Table:
#     PLAYER_ID - CHAR_ID - DATE - LP - MR

date = datetime.datetime.now()

charid_map: dict[int, str] = {
    1: "Ryu",
    2: "2",
    3: "3",
    4: "4",
    5: "Manon",
    6: "Zangief",
    7: "7",
    8: "Dhalsim",
    9: "Cammy",
    10: "Ken",
    11: "Dee Jay",
    12: "Lily",
    13: "13",
    14: "Rashid",
    15: "Blanka",
    16: "Juri",
    17: "Marisa",
    18: "Guile",
    19: "19",
    20: "E. Honda",
    21: "21",
    22: "22",
    23: "23",
}

historical_dates: list[tuple[int, int, int]] = [
    (2023, 12, 24),
    (2024, 1, 10),
    (2024, 1, 12),
    (2024, 5, 13),
    (2024, 5, 20),
]


class RecordedLP:

    def __init__(self, player_id, char_id, date_stats, lp, mr) -> None:
        self.player_id: str = player_id
        self.char_id: str = char_id
        self.date_stats: datetime.datetime = date_stats
        self.lp: int = lp
        self.mr: int = mr


def create_initial_database(filename):
    """creates initial database"""
    conn = None

    try:
        conn = sqlite3.connect(filename)
        print("creating db")
    except sqlite3.Error as e:
        print(e)
    finally:
        if conn:
            conn.close()


def create_ranking_table():
    """creates the ranking history table"""

    sql_statements = [
        """CREATE TABLE IF NOT EXISTS ranking (
            date TIMESTAMP NOT NULL,
            player_id TEXT NOT NULL,
            char_id TEXT NOT NULL,
            lp TEXT NOT NULL,
            mr TEXT,
            unique(player_id, char_id, date));"""
    ]

    try:
        with sqlite3.connect("cfn-stats.db") as conn:
            cursor = conn.cursor()
            for statement in sql_statements:
                cursor.execute(statement)

            conn.commit()
    except sqlite3.Error as e:
        print(e)


def insert_data(record: RecordedLP):
    """inserts data!"""

    try:
        with sqlite3.connect("cfn-stats.db") as conn:
            cursor = conn.cursor()

            insert_query = """INSERT INTO ranking VALUES (?, ?, ?, ?, ?);"""

            cursor.execute(
                insert_query,
                (
                    record.date_stats,
                    record.player_id,
                    record.char_id,
                    record.lp,
                    record.mr,
                ),
            )

            conn.commit()
            cursor.close()
    except sqlite3.Error as e:
        print(e)


def load_player_overview_data(player_id: str, req_date: datetime.datetime = date):
    """Loads the player's data and inserts it into the db"""
    overview_location = Path(
        f"cfn_stats/{str(req_date.year)}/{str(req_date.month)}/{str(req_date.day)}/"
        f"{player_id}/"
        f"{player_id}_overview.json"
    )

    try:
        with open(overview_location, "r", encoding="utf-8") as f:
            player_data: dict = json.loads(f.read())

            player_name: dict = player_data["pageProps"]["fighter_banner_info"][
                "personal_info"
            ]["fighter_id"]

            current_char_id: int = player_data["pageProps"]["fighter_banner_info"][
                "favorite_character_id"
            ]

            current_char: str = charid_map[current_char_id]

            current_rank: str = player_data["pageProps"]["fighter_banner_info"][
                "favorite_character_league_info"
            ]["league_rank_info"]["league_rank_name"]

            current_lp: str = player_data["pageProps"]["fighter_banner_info"][
                "favorite_character_league_info"
            ]["league_point"]

            print(
                f"{player_name} overview for {req_date}"
                "\n"
                f"Current character: {current_char} ({current_rank} {current_lp} LP)."
            )
            print()
    except FileNotFoundError:
        print(f"No player overview for {player_id} on {req_date}!")
        return

    player_record: RecordedLP = RecordedLP(
        player_id, current_char_id, req_date, current_lp, None
    )

    return player_record


def fill_out_historical_data():
    """Update the database with the select few days in the past."""

    for hist_date in historical_dates:
        player_ids = os.listdir(
            f"cfn_stats/{hist_date[0]}/{hist_date[1]}/{hist_date[2]}"
        )
        for player in player_ids:
            if len(player) == 10:
                data_to_insert = load_player_overview_data(
                    player, datetime.datetime(hist_date[0], hist_date[1], hist_date[2])
                )

                if data_to_insert:
                    insert_data(data_to_insert)


def update_todays_data():
    """Update the database with todays data."""

    player_ids = os.listdir(f"cfn_stats/{date.year}/{date.month}/{date.day}")

    for player in player_ids:
        if len(player) == 10:
            data_to_insert = load_player_overview_data(
                player, datetime.datetime(date.year, date.month, date.day)
            )

            if data_to_insert:
                insert_data(data_to_insert)


if __name__ == "__main__":
    create_initial_database("cfn-stats.db")
    create_ranking_table()
    fill_out_historical_data()
    update_todays_data()
