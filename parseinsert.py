"""Inserts the data from raw .json files into a SQLite db."""

import datetime
import json
import os
import sqlite3
from pathlib import Path

# Historical Trend Table:
#     PLAYER_ID - CHAR_ID - DATE - LP - MR

todays_datetime = datetime.datetime.now()

charid_map: dict[int, str] = {
    1: "Ryu",
    2: "Luke",
    3: "Kimberly",
    4: "Chun-Li",
    5: "Manon",
    6: "Zangief",
    7: "JP",
    8: "Dhalsim",
    9: "Cammy",
    10: "Ken",
    11: "Dee Jay",
    12: "Lily",
    13: "A.K.I.",
    14: "Rashid",
    15: "Blanka",
    16: "Juri",
    17: "Marisa",
    18: "Guile",
    19: "Ed",
    20: "E. Honda",
    21: "Jamie",
    22: "Akuma",
    23: "23",
    24: "24",
    25: "25",
    26: "M. Bison",
    27: "27",
    28: "28",
    29: "29",
    30: "30",
}

historical_dates: list[tuple[int, int, int]] = [
    (2023, 12, 24),
    (2024, 1, 10),
    (2024, 1, 12),
    (2024, 5, 13),
    (2024, 5, 20),
    (2024, 6, 10),
]


class RecordedLP:
    """The thing we return to record LP"""

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


def create_tables():
    """creates the tables"""

    sql_statements = [
        """CREATE TABLE IF NOT EXISTS ranking (
            date TIMESTAMP NOT NULL,
            player_id TEXT NOT NULL,
            char_id TEXT NOT NULL,
            lp TEXT NOT NULL,
            mr TEXT,
            unique(player_id, char_id, date));""",
        """CREATE TABLE IF NOT EXISTS club_members (
            club_id TEXT NOT NULL,
            player_name TEXT NOT NULL,
            player_id TEXT NOT NULL,
            joined_at TEXT NOT NULL,
            position TEXT NOT NULL,
            unique(club_id, player_id));""",
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


def load_player_overview_data(
    player_id: str, req_date: datetime.datetime = todays_datetime
):
    """Loads the player's data and inserts it into the db"""
    overview_location = Path(
        f"cfn_stats/{str(req_date.year)}/{str(req_date.month)}/{str(req_date.day)}/"
        f"{player_id}/"
        f"{player_id}_overview.json"
    )

    record_list = []

    try:
        with open(overview_location, "r", encoding="utf-8") as f:
            player_data: dict = json.loads(f.read())

            player_chars: dict = player_data["pageProps"]["play"][
                "character_league_infos"
            ]

            for char in player_chars:
                if char["league_info"]["league_point"] != -1:
                    record_list.append(
                        RecordedLP(
                            player_id,
                            char["character_id"],
                            req_date,
                            char["league_info"]["league_point"],
                            char["league_info"]["master_rating"],
                        )
                    )

    except FileNotFoundError:
        print(f"No player overview for {player_id} on {req_date}!")

    return record_list


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

                for record in data_to_insert:
                    insert_data(record)


def update_todays_data():
    """Update the database with todays overview data."""

    directories = os.listdir(
        f"cfn_stats/{todays_datetime.year}/{todays_datetime.month}/{todays_datetime.day}"
    )

    for dir_name in directories:
        if len(dir_name) == 10:
            data_to_insert = load_player_overview_data(
                dir_name,
                datetime.datetime(
                    todays_datetime.year, todays_datetime.month, todays_datetime.day
                ),
            )

            for record in data_to_insert:
                insert_data(record)


def update_member_list(club_id, req_date: datetime.datetime = todays_datetime):
    """Updates the club_members database with people loaded from FunnyAnimals"""
    club_data_location = Path(
        f"cfn_stats/{str(req_date.year)}/{str(req_date.month)}/{str(req_date.day)}/{club_id}/{club_id}.json"
    )

    member_list = []

    try:
        with open(club_data_location, "r", encoding="utf-8") as f:
            club_data: dict = json.loads(f.read())
            club_members = club_data["pageProps"]["circle_member_list"]

            for member in club_members:

                member_list.append(
                    (
                        member["fighter_banner_info"]["personal_info"]["fighter_id"],
                        str(member["fighter_banner_info"]["personal_info"]["short_id"]),
                        datetime.datetime.fromtimestamp(int(member["joined_at"])),
                        member["position"],
                    )
                )

            print(
                f"{club_data['pageProps']['circle_base_info']['name']} stats updated for {req_date}"
            )
        print()
    except FileNotFoundError:
        print(f"No club overview for {club_id} on {req_date}!")
        return

    try:
        with sqlite3.connect("cfn-stats.db") as conn:
            cursor = conn.cursor()

            for player_name, player_id, join_date, position in member_list:
                cursor.execute(
                    """INSERT INTO club_members VALUES (?, ?, ?, ?, ?);""",
                    (club_id, player_name, player_id, join_date, position),
                )

            conn.commit()
            cursor.close()
    except sqlite3.Error as e:
        print(e)


if __name__ == "__main__":
    # create_initial_database("cfn-stats.db")
    # create_tables()
    fill_out_historical_data()
    # update_todays_data()
    # update_member_list(cfn_secrets.DEFAULT_CLUB_ID)
