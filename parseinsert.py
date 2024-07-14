"""Inserts the data from raw .json files into a SQLite db."""

import dataclasses
import datetime
import json
import logging
import os
import sqlite3
import sys
from pathlib import Path
from zoneinfo import ZoneInfo

now_datetime = datetime.datetime.now(ZoneInfo("America/Los_Angeles"))

historical_dates: list[datetime.datetime] = [
    datetime.datetime(2024, 7, 12, 0, 0, 0, 0, ZoneInfo("America/Los_Angeles")),
    datetime.datetime(2024, 7, 11, 0, 0, 0, 0, ZoneInfo("America/Los_Angeles")),
    datetime.datetime(2024, 7, 10, 0, 0, 0, 0, ZoneInfo("America/Los_Angeles")),
    datetime.datetime(2024, 7, 9, 0, 0, 0, 0, ZoneInfo("America/Los_Angeles")),
    datetime.datetime(2024, 7, 8, 0, 0, 0, 0, ZoneInfo("America/Los_Angeles")),
    datetime.datetime(2024, 7, 7, 0, 0, 0, 0, ZoneInfo("America/Los_Angeles")),
    datetime.datetime(2024, 7, 6, 0, 0, 0, 0, ZoneInfo("America/Los_Angeles")),
    datetime.datetime(2024, 7, 5, 0, 0, 0, 0, ZoneInfo("America/Los_Angeles")),
    datetime.datetime(2024, 7, 2, 0, 0, 0, 0, ZoneInfo("America/Los_Angeles")),
    datetime.datetime(2024, 7, 1, 0, 0, 0, 0, ZoneInfo("America/Los_Angeles")),
    # first snags, very few players
    # datetime.datetime(2024, 5, 13, 0, 0, 0, 0, ZoneInfo("America/Los_Angeles")),
    # datetime.datetime(2024, 1, 12, 0, 0, 0, 0, ZoneInfo("America/Los_Angeles")),
    # datetime.datetime(2024, 1, 10, 0, 0, 0, 0, ZoneInfo("America/Los_Angeles")),
    # datetime.datetime(2023, 12, 24, 0, 0, 0, 0, ZoneInfo("America/Los_Angeles")),
]

logging.basicConfig()
logger = logging.getLogger("cfn-stats-scrape")
logger.setLevel(logging.INFO)


@dataclasses.dataclass
class RecordedLP:
    """The thing we return to record LP"""

    def __init__(self, player_id, char_id, date_stats, lp, mr) -> None:
        # pylint: disable-msg=too-many-arguments

        self.player_id: str = player_id
        self.char_id: str = char_id
        self.date_stats: datetime.datetime = date_stats.isoformat()
        self.lp: int = lp
        self.mr: int = mr


@dataclasses.dataclass
class HistoricStats:
    """Date: PlayerID: <all your stats>"""

    # pylint: disable=too-many-instance-attributes
    # This is a representation of the database row
    # I'm just going with One Big Row to Get Something Done
    # I'll change it when I need to change it

    date: str
    player_id: str
    player_name: str
    selected_char_id: str
    lp: int
    mr: int
    hub_matches: int
    ranked_matches: int
    casual_matches: int
    custom_matches: int
    hub_time: int
    ranked_time: int
    casual_time: int
    custom_time: int
    extreme_time: int
    versus_time: int
    practice_time: int
    arcade_time: int
    wt_time: int
    thumbs: int
    last_played: str
    profile_tagline: str
    title_text: str
    title_plate: str


def create_tables(debug_flag: bool):
    """creates the tables"""

    logger.debug("Creating tables")

    sql_statements = [
        """CREATE TABLE IF NOT EXISTS club_members (
            club_id TEXT NOT NULL,
            player_name TEXT NOT NULL,
            player_id TEXT NOT NULL,
            joined_at TIMESTAMP,
            position INTEGER NOT NULL,
            unique(club_id, player_id));""",
        """CREATE TABLE IF NOT EXISTS ranking (
            date TIMESTAMP NOT NULL,
            player_id TEXT NOT NULL,
            char_id TEXT NOT NULL,
            lp INTEGER,
            mr INTEGER,
            unique(player_id, char_id, date));""",
        """CREATE TABLE IF NOT EXISTS historic_stats (
            date TIMESTAMP date_rec NOT NULL,
            player_id TEXT NOT NULL,
            player_name TEXT NOT NULL,

            selected_char TEXT NOT NULL,
            lp INTEGER,
            mr INTEGER,

            hub_matches INTEGER,
            ranked_matches INTEGER,
            casual_matches INTEGER,
            custom_matches INTEGER,

            hub_time INTEGER,
            ranked_time INTEGER,
            casual_time INTEGER,
            custom_time INTEGER,
            extreme_time INTEGER,
            versus_time INTEGER,
            practice_time INTEGER,
            arcade_time INTEGER,
            wt_time INTEGER,

            thumbs INTEGER,
            last_played TIMESTAMP last_play_at NOT NULL,
            profile_tagline TEXT,
            title_text TEXT,
            title_plate TEXT,

            unique(date, player_id));""",
    ]

    table_name: str = "cfn-stats.db"

    if debug_flag:
        table_name = "cfn-stats-debug.db"
        logger.debug("Running in debug mode, creating debug table.")

    try:
        with sqlite3.connect(table_name) as conn:
            cursor = conn.cursor()
            for statement in sql_statements:
                cursor.execute(statement)

            conn.commit()
    except sqlite3.Error as e:
        logger.error(e)

    logger.debug("Tables successfully created. [SUCCESS]")


def insert_rankings_into_db(record: RecordedLP, debug_flag: bool) -> None:
    """Takes the RecordedLP object and inserts it into the ranking table."""

    table_name = "cfn-stats.db"

    if debug_flag:
        logger.debug("In debug mode, using debug db.")
        table_name = "cfn-stats-debug.db"

    try:
        with sqlite3.connect(table_name) as conn:
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
        logger.error(e)


def insert_historic_stats_into_db(record: HistoricStats, debug_flag: bool) -> None:
    """Takes the HistoricalStats object and inserts it into the historic_stats table."""

    table_name = "cfn-stats.db"

    if debug_flag:
        logger.debug("In debug mode, using debug db.")
        table_name = "cfn-stats-debug.db"

    try:
        with sqlite3.connect(table_name) as conn:
            cursor = conn.cursor()

            insert_query = """INSERT INTO historic_stats VALUES (?, ?, ?, ?, ?, ?, ?, \
                ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);"""

            cursor.execute(
                insert_query,
                (
                    record.date,
                    record.player_id,
                    record.player_name,
                    record.selected_char_id,
                    record.lp,
                    record.mr,
                    record.hub_matches,
                    record.ranked_matches,
                    record.casual_matches,
                    record.custom_matches,
                    record.hub_time,
                    record.ranked_time,
                    record.casual_time,
                    record.custom_time,
                    record.extreme_time,
                    record.versus_time,
                    record.practice_time,
                    record.arcade_time,
                    record.wt_time,
                    record.thumbs,
                    record.last_played,
                    record.profile_tagline,
                    record.title_text,
                    record.title_plate,
                ),
            )

            conn.commit()
            cursor.close()
    except sqlite3.Error as e:
        logger.error(e)


def load_player_overview_json(player_id: str, req_date: datetime.datetime) -> dict:
    """Loads the player's overview json and returns the content."""

    overview_location = Path(
        f"cfn_stats/{str(req_date.year)}/{str(req_date.month)}/{str(req_date.day)}/"
        f"{player_id}/"
        f"{player_id}_overview.json"
    )

    player_dict: dict = {}

    try:
        with open(overview_location, "r", encoding="utf-8") as f:
            player_dict = json.loads(f.read())
    except FileNotFoundError:
        logger.error("No player overview for %s on %s!", player_id, req_date)

    return player_dict


def build_rankings_data(
    player_dict: dict, player_id: str, req_date: datetime.datetime
) -> list[RecordedLP]:
    """Takes a player stats dict and builds the daily LP/MR tracking for all their characters."""

    player_dict = player_dict["pageProps"]

    player_chars: dict = player_dict["play"]["character_league_infos"]

    record_list: list[RecordedLP] = []
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

    return record_list


def build_historic_data(
    player_dict: dict, player_id: str, req_date: datetime.datetime
) -> list[HistoricStats]:
    """Takes a player stats dict and builds the HistoricalStats entry."""

    # pylint: disable=too-many-locals
    # there's a lot of things im tracking

    player_dict = player_dict["pageProps"]

    content_play_time_list: list[dict[str, int | str]] = player_dict["play"][
        "base_info"
    ]["content_play_time_list"]

    wt_time = ranked_time = casual_time = custom_time = hub_time = versus_time = (
        arcade_time
    ) = practice_time = extreme_time = 0

    for character in content_play_time_list:
        match character["content_type_name"]:
            case "World Tour":
                wt_time = int(character["play_time"])
            case "Ranked Matches":
                ranked_time = int(character["play_time"])
            case "Casual Matches":
                casual_time = int(character["play_time"])
            case "Custom Room Matches":
                custom_time = int(character["play_time"])
            case "Battle Hub":
                hub_time = int(character["play_time"])
            case "Offline Matches":
                versus_time = int(character["play_time"])
            case "Arcade":
                arcade_time = int(character["play_time"])
            case "Practice":
                practice_time = int(character["play_time"])
            case "Extreme":
                extreme_time = int(character["play_time"])
            case _:
                print("ERROR: How did you get here??")

    player_name = str(player_dict["fighter_banner_info"]["personal_info"]["fighter_id"])
    fav_char_id = str(player_dict["fighter_banner_info"]["favorite_character_id"])
    fav_char_lp: int = player_dict["fighter_banner_info"][
        "favorite_character_league_info"
    ]["league_point"]

    fav_char_mr = int(
        player_dict["fighter_banner_info"]["favorite_character_league_info"][
            "master_rating"
        ]
    )
    hub_matches = int(
        player_dict["play"]["battle_stats"]["battle_hub_match_play_count"]
    )
    rank_matches = int(player_dict["play"]["battle_stats"]["rank_match_play_count"])
    casual_matches = int(player_dict["play"]["battle_stats"]["casual_match_play_count"])
    custom_matches = int(
        player_dict["play"]["battle_stats"]["custom_room_match_play_count"]
    )

    thumbs = int(player_dict["play"]["base_info"]["enjoy_total_point"])
    last_played = datetime.datetime.fromtimestamp(
        int(player_dict["fighter_banner_info"]["last_play_at"]),
        tz=ZoneInfo("America/Los_Angeles"),
    ).isoformat()
    profile_tagline = ""  # TODO: have to parse {{mesage1}} from JSON code
    title_text = str(player_dict["fighter_banner_info"]["title_data"]["title_data_val"])
    title_plate = str(
        player_dict["fighter_banner_info"]["title_data"]["title_data_plate_name"]
    )

    return [
        HistoricStats(
            req_date.isoformat(),
            player_id,
            player_name,
            fav_char_id,
            fav_char_lp,
            fav_char_mr,
            hub_matches,
            rank_matches,
            casual_matches,
            custom_matches,
            hub_time,
            ranked_time,
            casual_time,
            custom_time,
            extreme_time,
            versus_time,
            practice_time,
            arcade_time,
            wt_time,
            thumbs,
            last_played,
            profile_tagline,  # empty for now
            title_text,
            title_plate,
        )
    ]


def rebuild_database_from_local(debug_flag: bool) -> None:
    """Update the database with the select few days in the past."""

    logger.debug("Attempting %d days of past data.", len(historical_dates))

    for hist_date in historical_dates:
        update_stats_for_date(hist_date, debug_flag)


def update_stats_for_date(req_date: datetime.datetime, debug_flag: bool) -> None:
    """Update the database with todays overview data."""

    player_stat_dirs = os.listdir(
        f"cfn_stats/{req_date.year}/{req_date.month}/{req_date.day}"
    )

    if len(player_stat_dirs) == 0:
        logger.warning("There's no data for today %s!", req_date.strftime("%b %d %Y"))
        return

    all_player_json: dict[str, dict] = {}

    for player_id in player_stat_dirs:
        logger.debug("Going through player_id: %s", player_id)
        if len(player_id) != 10:
            logger.debug("Not a player: %s", player_id)
            continue

        # This is the object we calculate stats on
        player_data_dict = load_player_overview_json(player_id, req_date)
        all_player_json[player_id] = player_data_dict  # do i need this?

        # Gather each player's LP/MR for the date
        ranking_rows = build_rankings_data(player_data_dict, player_id, req_date)
        for rank_row in ranking_rows:
            insert_rankings_into_db(rank_row, debug_flag)

        # Gather player's HistoricStats for the date
        historic_rows = build_historic_data(player_data_dict, player_id, req_date)
        for hist_row in historic_rows:
            insert_historic_stats_into_db(hist_row, debug_flag)

    logger.info(
        "Data (possibly) inserted to db for: %s. [SUCCESS]",
        req_date.strftime("%b %d %Y"),
    )


def update_member_list(club_id, debug_flag: bool) -> None:
    """Updates the club_members database with people loaded from FunnyAnimals"""

    club_data_location = Path(
        f"cfn_stats/{str(now_datetime.year)}/{str(now_datetime.month)}/{str(now_datetime.day)}/{club_id}/{club_id}.json"
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
                            tz=ZoneInfo("America/Los_Angeles"),
                        ).isoformat(),
                        int(member["position"]),
                    )
                )
    except FileNotFoundError:
        logger.error("No club overview for %s!", club_id)
        return

    table_name = "cfn-stats.db"
    if debug_flag:
        logger.debug("Running in debug mode, using debug db.")
        table_name = "cfn-stats-debug.db"

    try:
        with sqlite3.connect(table_name) as conn:
            cursor = conn.cursor()

            for player_name, player_id, join_date, position in member_list:
                cursor.execute(
                    """INSERT INTO club_members VALUES (?, ?, ?, ?, ?);""",
                    (club_id, player_name, player_id, join_date, position),
                )

            conn.commit()
            cursor.close()
    except sqlite3.Error as e:
        logger.error(e)

    logger.info("Updating member list: [SUCCESS]")


if __name__ == "__main__":
    if len(sys.argv) == 1:
        print("No arguments supplied!")
        print("-debug -new -club -hist -daily")

    DEBUG_FLAG = False

    if "-debug" in sys.argv[1:]:
        DEBUG_FLAG = True
        logger.setLevel(logging.DEBUG)
        logger.debug("***** ***** DEBUG ENABLED will not enter SQL to database.")

    if "-new" in sys.argv[1:]:
        logger.debug("**** CREATING NEW TABLES")
        create_tables(debug_flag=DEBUG_FLAG)

    if "-club" in sys.argv[1:]:
        logger.debug("**** UPDATING CLUB INFO")
        update_member_list("c984cc7ce8cd44b9a209e984a73d0c9e", debug_flag=DEBUG_FLAG)

    if "-hist" in sys.argv[1:]:
        logger.debug("**** REBUILDING PAST DATA")
        rebuild_database_from_local(debug_flag=DEBUG_FLAG)

    if "-daily" in sys.argv[1:]:
        logger.debug("**** DAILY RUN")
        update_stats_for_date(now_datetime, debug_flag=DEBUG_FLAG)
