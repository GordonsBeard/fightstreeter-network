"""Inserts the data from raw .json files into a SQLite db."""

import dataclasses
import datetime
import glob
import json
import logging
import os
import sqlite3
from pathlib import Path
from zoneinfo import ZoneInfo

from notify_run import Notify  # type: ignore

logging.basicConfig()
logger = logging.getLogger("cfn-stats-scrape")
logger.setLevel(logging.INFO)


def split_all(path) -> list[str]:
    """Stolen code that splits the path instead of learning a smart way of doing this"""
    allparts: list[str] = []

    while True:
        parts = os.path.split(path)
        if parts[0] == path:
            allparts.insert(0, parts[0])
            break
        if parts[1] == path:
            allparts.insert(0, parts[1])
            break
        path = parts[0]
        allparts.insert(0, parts[1])

    return allparts


@dataclasses.dataclass
class RecordedLP:
    """The thing we return to record LP"""

    def __init__(self, player_id, char_id, date_stats, phase, lp, mr) -> None:
        self.player_id: str = player_id
        self.char_id: str = char_id
        self.date_stats: datetime.datetime = date_stats
        self.phase: int = phase
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
    total_kudos: int
    thumbs: int
    last_played: str
    profile_tagline: str
    title_text: str
    title_plate: str


class CFNStatsParser:
    """Object that stuffs the .json into sqlite"""

    cfn_path = os.path.join("cfn_stats", "20*", "*", "*")
    dates_to_restore = list(glob.glob(cfn_path))
    historical_dates = []
    now_datetime = datetime.datetime.now(ZoneInfo("America/Los_Angeles")).replace(
        microsecond=0, second=0, minute=0, hour=12
    )

    for date in dates_to_restore:
        date_vals = split_all(date)
        dt = datetime.datetime(
            year=int(date_vals[1]), month=int(date_vals[2]), day=int(date_vals[3])
        )
        historical_dates.append(dt)

    def __init__(self, debug_flag: bool, notify_channel: str) -> None:
        self.debug_flag: bool = debug_flag
        self.notify: Notify = Notify(notify_channel)

        if debug_flag:
            logger.setLevel(logging.DEBUG)

    def send_push_alert(self, message) -> None:
        """This will send a notify.run alert."""
        self.notify.send(message)

    def update_stats_for_date(self, req_date: datetime.datetime) -> None:
        """Update the database with a given date's overview data."""

        player_stat_dirs = os.listdir(
            f"cfn_stats/{req_date.year}/{req_date.month}/{req_date.day}"
        )

        if len(player_stat_dirs) == 0:
            logger.warning(
                "There's no data for today %s!", req_date.strftime("%b %d %Y")
            )
            return

        for player_id in player_stat_dirs:
            logger.debug("Going through player_id: %s", player_id)
            if len(player_id) != 10:
                logger.debug("Not a player: %s", player_id)
                continue

            # This is the object we calculate stats on
            player_data_dict = self.load_player_overview_json(player_id, req_date)

            # Gather each player's LP/MR for the date
            ranking_rows = self.build_rankings_data(
                player_data_dict, player_id, req_date
            )
            for rank_row in ranking_rows:
                self.insert_rankings_into_db(rank_row)

            # Gather player's HistoricStats for the date
            historic_rows = self.build_historic_data(
                player_data_dict, player_id, req_date
            )
            for hist_row in historic_rows:
                self.insert_historic_stats_into_db(hist_row)

        logger.info(
            "Data (possibly) inserted to db for: %s. [SUCCESS]",
            req_date.strftime("%b %d %Y"),
        )

    def insert_rankings_into_db(self, record: RecordedLP) -> None:
        """Takes the RecordedLP object and inserts it into the ranking table."""

        table_name = "instance/cfn-stats.db"

        if self.debug_flag:
            logger.debug("In debug mode, using debug db.")
            table_name = "cfn-stats-debug.db"

        try:
            with sqlite3.connect(table_name) as conn:
                cursor = conn.cursor()

                insert_query = """INSERT INTO ranking VALUES (?, ?, ?, ?, ?, ?);"""

                cursor.execute(
                    insert_query,
                    (
                        record.date_stats,
                        record.phase,
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

    def insert_historic_stats_into_db(self, record: HistoricStats) -> None:
        """Takes the HistoricalStats object and inserts it into the historic_stats table."""

        table_name = "instance/cfn-stats.db"

        if self.debug_flag:
            logger.debug("In debug mode, using debug db.")
            table_name = "cfn-stats-debug.db"

        try:
            with sqlite3.connect(table_name) as conn:
                cursor = conn.cursor()

                insert_query = """INSERT INTO historic_stats VALUES (?, ?, ?, ?, ?, ?, ?, \
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);"""

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
                        record.total_kudos,
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

    def load_player_overview_json(
        self, player_id: str, req_date: datetime.datetime
    ) -> dict:
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
        self, player_dict: dict, player_id: str, req_date: datetime.datetime
    ) -> list[RecordedLP]:
        """Takes a player stats dict and builds the daily LP/MR tracking for all their characters."""

        player_dict = player_dict["pageProps"]

        player_chars: dict = player_dict["play"]["character_league_infos"]
        phase: int = player_dict["play"]["current_season_id"]

        record_list: list[RecordedLP] = []
        for char in player_chars:
            if char["league_info"]["league_point"] > 0:
                record_list.append(
                    RecordedLP(
                        str(player_id),
                        str(char["character_id"]),
                        req_date.strftime("%Y-%m-%d"),
                        phase,
                        int(char["league_info"]["league_point"]),
                        int(char["league_info"]["master_rating"]),
                    )
                )

        return record_list

    def build_historic_data(
        self, player_dict: dict, player_id: str, req_date: datetime.datetime
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

        player_name = str(
            player_dict["fighter_banner_info"]["personal_info"]["fighter_id"]
        )
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
        casual_matches = int(
            player_dict["play"]["battle_stats"]["casual_match_play_count"]
        )
        custom_matches = int(
            player_dict["play"]["battle_stats"]["custom_room_match_play_count"]
        )
        total_kudos = int(
            player_dict["play"]["battle_stats"]["total_all_character_play_point"]
        )
        thumbs = int(player_dict["play"]["base_info"]["enjoy_total_point"])
        last_played = datetime.datetime.fromtimestamp(
            int(player_dict["fighter_banner_info"]["last_play_at"]),
            tz=ZoneInfo("America/Los_Angeles"),
        ).strftime("%Y-%m-%d")
        title_text = str(
            player_dict["fighter_banner_info"]["title_data"]["title_data_val"]
        )
        title_plate = str(
            player_dict["fighter_banner_info"]["title_data"]["title_data_plate_name"]
        )

        profile_tag_name = str(
            player_dict["fighter_banner_info"]["profile_comment"]["profile_tag_name"]
        )
        profile_tag_option = str(
            player_dict["fighter_banner_info"]["profile_comment"]["profile_tag_option"]
        )
        profile_tagline = profile_tag_name.replace("{{message1}}", profile_tag_option)

        return [
            HistoricStats(
                req_date.strftime("%Y-%m-%d"),
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
                total_kudos,
                thumbs,
                last_played,
                profile_tagline,
                title_text,
                title_plate,
            )
        ]

    def update_member_list(self, club_id) -> None:
        """Updates the club_members database with people loaded from FunnyAnimals"""
        logger.debug("**** UPDATING CLUB INFO")
        club_data_location = Path(
            f"cfn_stats/{str(self.now_datetime.year)}/{str(self.now_datetime.month)}"
            f"/{str(self.now_datetime.day)}/{club_id}/{club_id}.json"
        )

        # Initialize the club members and put Shay first because he's not in the club
        member_list: list[tuple[str, str, str | None, int]] = [
            # (
            #     "Shaymoo",
            #     "3022660117",
            #     None,
            #     3,
            # )
        ]

        try:
            with open(club_data_location, "r", encoding="utf-8") as f:
                club_data: dict = json.loads(f.read())
                club_members = club_data["pageProps"]["circle_member_list"]

                for member in club_members:

                    member_list.append(
                        (
                            str(
                                member["fighter_banner_info"]["personal_info"][
                                    "fighter_id"
                                ]
                            ),
                            str(
                                member["fighter_banner_info"]["personal_info"][
                                    "short_id"
                                ]
                            ),
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

        table_name = "instance/cfn-stats.db"
        if self.debug_flag:
            logger.debug("Running in debug mode, using debug db.")
            table_name = "cfn-stats-debug.db"

        try:
            with sqlite3.connect(table_name) as conn:
                cursor = conn.cursor()

                for player_name, player_id, join_date, position in member_list:
                    hidden = 1 if player_id == "3022660117" else 0
                    cursor.execute(
                        """INSERT INTO club_members VALUES (?, ?, ?, ?, ?, ?);""",
                        (club_id, player_name, player_id, join_date, position, hidden),
                    )

                conn.commit()
                cursor.close()
        except sqlite3.Error as e:
            logger.error(e)

        logger.info("Updating member list: [SUCCESS]")
