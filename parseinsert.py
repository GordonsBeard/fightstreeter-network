"""Inserts the data from raw .json files into a SQLite db."""

import datetime
import json
import os
import sqlite3
from pathlib import Path

import pytz

todays_datetime = datetime.datetime.now(tz=pytz.timezone("America/Los_Angeles"))

historical_dates: list[tuple[int, int, int]] = [
    # (2023, 12, 24),
    # (2024, 1, 10),
    # (2024, 1, 12),
    # (2024, 5, 13),
    (2024, 7, 1),
    (2024, 7, 2),
    (2024, 7, 5),
    (2024, 7, 6),
    (2024, 7, 7),
    (2024, 7, 8),
    (2024, 7, 9),
    (2024, 7, 10),
]


class RecordedLP:
    """The thing we return to record LP"""

    def __init__(self, player_id, char_id, date_stats, lp, mr) -> None:
        self.player_id: str = player_id
        self.char_id: str = char_id
        self.date_stats: datetime.datetime = date_stats.isoformat()
        self.lp: int = lp
        self.mr: int = mr


def create_tables():
    """creates the tables"""

    sql_statements = [
        """CREATE TABLE IF NOT EXISTS ranking (
            date TIMESTAMP NOT NULL,
            player_id TEXT NOT NULL,
            char_id TEXT NOT NULL,
            lp INTEGER,
            mr INTEGER,
            unique(player_id, char_id, date));""",
        """CREATE TABLE IF NOT EXISTS club_members (
            club_id TEXT NOT NULL,
            player_name TEXT NOT NULL,
            player_id TEXT NOT NULL,
            joined_at TIMESTAMP,
            position INTEGER NOT NULL,
            unique(club_id, player_id));""",
        """CREATE TABLE IF NOT EXISTS historic_stats (
            date TIMESTAMP NOT NULL,
            player_id TEXT NOT NULL,
            player_name TEXT NOT NULL,

            selected_char TEXT NOT NULL,
            lp INTEGER,
            mr INTEGER,

            hub_matches INTEGER,
            ranked_matches INTEGER,
            casual_matches INTEGER,
            room_matches INTEGER,
            extreme_matches INTEGER,
            local_matches INTEGER,

            hub_time INTEGER,
            ranked_time INTEGER,
            casual_time INTEGER,
            room_time INTEGER,
            extreme_time INTEGER,
            practice_time INTEGER,
            arcade_time INTEGER,
            wt_time INTEGER,

            thumbs INTEGER,
            last_played TIMESTAMP last_play_at,
            profile_tagline TEXT,
            title_text TEXT,
            title_plate TEXT,

            unique(date, player_id));""",
    ]

    try:
        print("Creating new tables.")
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


def load_player_overview_json(
    player_id: str, req_date: datetime.datetime = todays_datetime
) -> list[RecordedLP]:
    """Loads the player's over json and builds/returns the RecordedLP object."""
    overview_location = Path(
        f"cfn_stats/{str(req_date.year)}/{str(req_date.month)}/{str(req_date.day)}/"
        f"{player_id}/"
        f"{player_id}_overview.json"
    )

    record_list: list[RecordedLP] = []

    try:
        with open(overview_location, "r", encoding="utf-8") as f:
            player_data: dict = json.loads(f.read())

            player_chars: dict = player_data["pageProps"]["play"][
                "character_league_infos"
            ]

            for char in player_chars:
                if char["league_info"]["league_point"] > 0:
                    record_list.append(
                        RecordedLP(
                            str(player_id),
                            str(char["character_id"]),
                            req_date,
                            int(char["league_info"]["league_point"]),
                            int(char["league_info"]["master_rating"]),
                        )
                    )

    except FileNotFoundError:
        print(f"No player overview for {player_id} on {req_date}!")

    return record_list


def fill_out_historical_data() -> None:
    """Update the database with the select few days in the past."""

    print(f"Updating {len(historical_dates)} days of historical data.")

    for hist_date in historical_dates:
        req_date = datetime.datetime.strptime(
            f"{hist_date[0]}/{hist_date[1]}/{hist_date[2]}", "%Y/%m/%d"
        ).replace(tzinfo=pytz.timezone("America/Los_Angeles"))

        update_stats_for_date(req_date)

    print("Historical data inserted.")


def update_stats_for_date(req_date: datetime.datetime) -> None:
    """Update the database with todays overview data."""
    print(f"Updating stats for: {req_date}")

    player_stat_dirs = os.listdir(
        f"cfn_stats/{req_date.year}/{req_date.month}/{req_date.day}"
    )

    if len(player_stat_dirs) == 0:
        print(f"There's no data for {req_date}, aborting.")
        return

    for dir_name in player_stat_dirs:
        if len(dir_name) == 10:
            data_to_insert = load_player_overview_json(
                dir_name,
                datetime.datetime(
                    req_date.year,
                    req_date.month,
                    req_date.day,
                    tzinfo=pytz.timezone("America/Los_Angeles"),
                ),
            )

            for record in data_to_insert:
                insert_data(record)

    print(f"Data inserted to db for: {req_date}")


def update_member_list(club_id, req_date: datetime.datetime = todays_datetime) -> None:
    """Updates the club_members database with people loaded from FunnyAnimals"""
    club_data_location = Path(
        f"cfn_stats/{str(req_date.year)}/{str(req_date.month)}/{str(req_date.day)}/{club_id}/{club_id}.json"
    )

    # Initialize the club members and put Shay first because he's not in the club
    member_list: list[tuple[str, str, str | None, int]] = [
        (
            "Shaymoo",
            "3022660117",
            None,
            3,
        )
    ]

    try:
        with open(club_data_location, "r", encoding="utf-8") as f:
            club_data: dict = json.loads(f.read())
            club_members = club_data["pageProps"]["circle_member_list"]

            for member in club_members:

                member_list.append(
                    (
                        str(
                            member["fighter_banner_info"]["personal_info"]["fighter_id"]
                        ),
                        str(member["fighter_banner_info"]["personal_info"]["short_id"]),
                        datetime.datetime.fromtimestamp(
                            int(member["joined_at"]),
                            tz=pytz.timezone("America/Los_Angeles"),
                        ).isoformat(),
                        int(member["position"]),
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

    print("Member list updated.")


if __name__ == "__main__":
    create_tables()
    update_member_list("c984cc7ce8cd44b9a209e984a73d0c9e")
    fill_out_historical_data()
    update_stats_for_date(todays_datetime)
    print("Complete.")
