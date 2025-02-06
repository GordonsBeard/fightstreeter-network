"""Module providing for the scraping of CFN for player stats"""

import json
import logging
import sys
import time
from datetime import datetime
from enum import Enum
from pathlib import Path
from zoneinfo import ZoneInfo

import requests
from notify_run import Notify  # type: ignore

import cfn_secrets
import cookieread
from constants import FUNNY_ANIMALS
from last_updated import log_last_update, start_last_update

logging.basicConfig()
logger = logging.getLogger("cfn-stats-scrape")
logger.setLevel(logging.INFO)

MISSING_ID_MATCHES = "Missing player_id, cannot build request url for matches."
MISSING_ID_DATA = "Missing player_id, cannot build request url for data."
MISSING_CLUB_ID = "Missing club_id, cannot build reqeuest url for data."


class Subject(Enum):
    """Subject of the data scraper's data scraping."""

    OVERVIEW = 1
    STATS = 2
    AVATAR = 3
    CLUB = 4
    ALL_MATCHES = 5
    RANKED_MATCHES = 6
    CASUAL_MATCHES = 7
    CUSTOM_MATCHES = 8
    HUB_MATCHES = 9


class CFNStatsScraper:
    """Object that grabs the data from the website"""

    _url_token: str = cfn_secrets.URL_TOKEN
    _buckler_id = cookieread.BUCKLER_ID
    _buckler_r_id = cookieread.BUCKLER_R_ID
    _buckler_praise_date = cookieread.BUCKLER_PRAISE_DATE

    def __init__(self, date: datetime, debug_flag: bool) -> None:
        self.debug: bool = debug_flag
        self.date: datetime = date
        self._player_id: str = ""
        self._club_id: str = ""
        self._page_no: int = 1
        self._full_battlelog: bool = False
        self._no_more_fetch: bool = False
        self.notify = Notify(cfn_secrets.NOTIFY_CHANNEL)

        base_cache_dir: str = (
            f"cfn_stats/{str(self.date.year)}/{str(self.date.month)}/{str(self.date.day)}"
            if not debug_flag
            else f"cfn_stats/mock/{str(self.date.year)}/{str(self.date.month)}/{str(self.date.day)}"
        )

        self.base_cache_dir: Path = Path(base_cache_dir)

        if debug_flag:
            logger.setLevel(logging.DEBUG)

    def send_push_alert(self, message) -> None:
        """This will send a notify.run alert."""
        self.notify.send(message)

    @property
    def player_id(self) -> str:
        """Player's CFN ID."""
        return self._player_id

    @player_id.setter
    def player_id(self, player_id) -> None:
        """Setter for Player's CFN ID."""
        self._player_id = player_id

    @property
    def club_id(self) -> str:
        """Club's CFN ID."""
        return self._club_id

    @club_id.setter
    def club_id(self, club_id: str) -> None:
        """Setter for club's CFN ID."""
        self._club_id = club_id

    @property
    def page_number(self) -> int:
        """Current page number of battlelog to fetch."""
        return self._page_no

    @page_number.setter
    def page_number(self, page_num: int) -> None:
        """Setter for battlelog page number."""
        self._page_no = page_num

    def _cache_dir(self, subject: Subject) -> Path:
        """Returns the path for the cached json."""

        match subject:
            case (
                Subject.OVERVIEW
                | Subject.STATS
                | Subject.AVATAR
                | Subject.ALL_MATCHES
                | Subject.RANKED_MATCHES
                | Subject.CASUAL_MATCHES
                | Subject.CUSTOM_MATCHES
                | Subject.HUB_MATCHES
            ):
                return Path(self.base_cache_dir / self.player_id)
            case Subject.CLUB:
                return Path(self.base_cache_dir / self.club_id)
            case _:
                raise NotImplementedError(
                    f"{subject.name} not implemented in _cache_dir()"
                )

    def _cache_filename(self, subject: Subject) -> Path:
        """Returns the filename for the cached json."""

        match subject:
            case Subject.OVERVIEW:
                return Path(
                    self._cache_dir(Subject.OVERVIEW)
                    / f"{self.player_id}_overview.json"
                )
            case Subject.CLUB:
                return Path(self._cache_dir(Subject.CLUB) / f"{self.club_id}.json")
            case Subject.STATS:
                return Path(
                    self._cache_dir(Subject.STATS) / f"{self.player_id}_play.json"
                )
            case Subject.AVATAR:
                return Path(
                    self._cache_dir(Subject.AVATAR) / f"{self.player_id}_avatar.json"
                )
            case Subject.ALL_MATCHES:
                return Path(
                    self._cache_dir(Subject.ALL_MATCHES)
                    / f"{self.player_id}_battlelog_{self.page_number:02d}.json"
                )
            case Subject.RANKED_MATCHES:
                return Path(
                    self._cache_dir(Subject.RANKED_MATCHES)
                    / f"{self.player_id}_battlelog_rank_{self.page_number:02d}.json"
                )
            case Subject.CASUAL_MATCHES:
                return Path(
                    self._cache_dir(Subject.CASUAL_MATCHES)
                    / f"{self.player_id}_battlelog_casual_{self.page_number:02d}.json"
                )
            case Subject.CUSTOM_MATCHES:
                return Path(
                    self._cache_dir(Subject.CUSTOM_MATCHES)
                    / f"{self.player_id}_battlelog_custom_{self.page_number:02d}.json"
                )
            case Subject.HUB_MATCHES:
                return Path(
                    self._cache_dir(Subject.HUB_MATCHES)
                    / f"{self.player_id}_battlelog_hub_{self.page_number:02d}.json"
                )
            case _:
                raise NotImplementedError(
                    f"{subject.name} not implemented in _cache_filename()"
                )

    def _get_req_url(self, subject: Subject) -> str:
        """Returns the request URL for a given subject."""
        match subject:
            case Subject.OVERVIEW:
                if not self.player_id:
                    self.send_push_alert(MISSING_ID_DATA)
                    sys.exit(MISSING_ID_DATA)

                return (
                    "https://www.streetfighter.com/6/buckler/_next/data"
                    f"/{self._url_token}/en/profile"
                    f"/{self.player_id}.json?sid={self.player_id}"
                )
            case Subject.CLUB:
                if not self.club_id:
                    self.send_push_alert(MISSING_CLUB_ID)
                    sys.exit(MISSING_CLUB_ID)

                return (
                    "https://www.streetfighter.com/6/buckler/_next/data"
                    f"/{self._url_token}/en/club"
                    f"/{self.club_id}.json?clubid={self.club_id}"
                )
            case Subject.STATS:
                if not self.player_id:
                    self.send_push_alert(MISSING_ID_DATA)
                    sys.exit(MISSING_ID_DATA)

                return (
                    "https://www.streetfighter.com/6/buckler/_next/data"
                    f"/{self._url_token}/en/profile"
                    f"/{self.player_id}/play.json?sid={self.player_id}"
                )
            case Subject.AVATAR:
                if not self.player_id:
                    self.send_push_alert(MISSING_ID_DATA)
                    sys.exit(MISSING_ID_DATA)

                return (
                    "https://www.streetfighter.com/6/buckler/_next/data"
                    f"/{self._url_token}/en/profile"
                    f"/{self.player_id}/avatar.json?sid={self.player_id}"
                )
            case Subject.ALL_MATCHES:
                if not self.player_id:
                    self.send_push_alert(MISSING_ID_MATCHES)
                    sys.exit(MISSING_ID_MATCHES)

                return (
                    "https://www.streetfighter.com/6/buckler/_next/data"
                    f"/{self._url_token}/en/profile"
                    f"/{self.player_id}/battlelog.json?page={self.page_number}&sid={self.player_id}"
                )
            case Subject.RANKED_MATCHES:
                if not self.player_id:
                    self.send_push_alert(MISSING_ID_MATCHES)
                    sys.exit(MISSING_ID_MATCHES)

                return (
                    "https://www.streetfighter.com/6/buckler/_next/data"
                    f"/{self._url_token}/en/profile"
                    f"/{self.player_id}/battlelog/rank.json?page={self.page_number}&sid={self.player_id}"
                )
            case Subject.CASUAL_MATCHES:
                if not self.player_id:
                    self.send_push_alert(MISSING_ID_MATCHES)
                    sys.exit(MISSING_ID_MATCHES)

                return (
                    "https://www.streetfighter.com/6/buckler/_next/data"
                    f"/{self._url_token}/en/profile"
                    f"/{self.player_id}/battlelog/casual.json?page={self.page_number}&sid={self.player_id}"
                )
            case Subject.CUSTOM_MATCHES:
                if not self.player_id:
                    self.send_push_alert(MISSING_ID_MATCHES)
                    sys.exit(MISSING_ID_MATCHES)

                return (
                    "https://www.streetfighter.com/6/buckler/_next/data"
                    f"/{self._url_token}/en/profile"
                    f"/{self.player_id}/battlelog/custom.json?page={self.page_number}&sid={self.player_id}"
                )
            case Subject.HUB_MATCHES:
                if not self.player_id:
                    self.send_push_alert(MISSING_ID_MATCHES)
                    sys.exit(MISSING_ID_MATCHES)

                return (
                    "https://www.streetfighter.com/6/buckler/_next/data"
                    f"/{self._url_token}/en/profile"
                    f"/{self.player_id}/battlelog/hub.json?page={self.page_number}&sid={self.player_id}"
                )
            case _:
                raise NotImplementedError(
                    f"{subject.name} not implemented in _get_req_url()"
                )

    def _fetch_json(self, subject: Subject) -> dict:
        """Grabs the json object for the request subject. Cache or HTTP hit."""

        cached_data = self._load_cached_data(subject)

        if cached_data:
            logger.debug("Cached data found.")
            return cached_data

        if self.date.date() < datetime.today().date():
            logger.error(
                "[ERROR] Cannot request new data from a time before today! Halting."
            )
            self.send_push_alert(
                "Cannot request new data from a time before today! Halting."
            )
            sys.exit()

        cookies: dict[str, str] = {
            "buckler_id": self._buckler_id,
            "buckler_r_id": self._buckler_r_id,
            "buckler_praise_date": self._buckler_praise_date,
        }

        headers: dict[str, str] = {
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-US,en,q=0.9",
            "Cache-Content": "no-cache",
            "Connection": "keep-alive",
            "Host": "www.streetfighter.com",
            "Pragma": "no-cache",
            "Referer": f"https://www.streetfighter.com/6/buckler/profile/{cfn_secrets.DEFAULT_PLAYER_ID}/play",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
        }

        logger.debug("Making request for new data.")

        response: requests.Response = requests.get(
            self._get_req_url(subject),
            timeout=5,
            headers=headers,
            cookies=cookies,
        )

        logger.debug("Url attempted: %s", response.url)

        if response.status_code != 200:
            bad_request: str = f"Bad request! Status code: {response.status_code}"
            logger.error(bad_request)
            self.send_push_alert(bad_request)
            sys.exit()

        json_data: dict = response.json()

        # Store it for cache purposes
        self._store_json(json_data, subject)

        return json_data

    def _verify_json(self, json_data: dict, subject: Subject) -> bool:
        """Does sanity checks on the keys expected in the json data."""

        if not json_data:
            empty_json: str = f"{subject.name} json is empty. Aborting."
            logger.error(empty_json)
            self.send_push_alert(empty_json)
            sys.exit()

        if "pageProps" not in json_data:
            missing_props: str = (
                "{subject.name} json is missing root 'pageProps' element. Aborting."
            )
            logger.error(missing_props)
            self.send_push_alert(missing_props)
            sys.exit()

        req_profile_keys: list[str] = ["fighter_banner_info", "play"]

        match subject:
            case Subject.OVERVIEW:
                if not all(k in json_data["pageProps"] for k in req_profile_keys):
                    missing_key: str = (
                        "{subject.name} json is missing a required stats key. Aborting."
                    )
                    logger.error(missing_key)
                    self.send_push_alert(missing_key)
                    sys.exit()
                req_ov_keys: list[str] = [
                    "base_info",
                    "battle_stats",
                    "character_league_infos",
                    "character_play_point_infos",
                    "character_win_rates",
                    "character_win_rates_by_rival_character",
                    "current_season_id",
                    "season_ids",
                ]
                if not all(k in json_data["pageProps"]["play"] for k in req_ov_keys):
                    data_incomplete: str = (
                        f"{subject.name} data is incomplete, missing keys in 'play' section. Aborting."
                    )
                    self.send_push_alert(data_incomplete)
                    logger.error(data_incomplete)
                    sys.exit()
            case Subject.CLUB:
                req_club_keys: list[str] = [
                    "circle_base_info",
                    "circle_member_list",
                    "circle_timeline_list",
                ]
                if not all(k in json_data["pageProps"] for k in req_club_keys):
                    missing_keys: str = (
                        f"{subject.name} json is missing a required stats key. Aborting."
                    )
                    logger.error(missing_keys)
                    self.send_push_alert(missing_keys)
                    sys.exit()
            case Subject.STATS:
                if not all(k in json_data["pageProps"] for k in req_profile_keys):
                    missing_prof: str = (
                        f"{subject.name} json is missing a required stats key. Aborting."
                    )
                    logger.error(missing_prof)
                    self.send_push_alert(missing_prof)
                    sys.exit()
                req_battle_keys: list[str] = [
                    "base_info",
                    "battle_stats",
                    "character_league_infos",
                    "character_play_point_infos",
                    "character_win_rates",
                    "character_win_rates_by_rival_character",
                    "current_season_id",
                    "season_ids",
                ]
                if not all(
                    k in json_data["pageProps"]["play"] for k in req_battle_keys
                ):
                    missing_play: str = (
                        f"{subject.name} json is missing a required play key. Aborting."
                    )
                    self.send_push_alert(missing_play)
                    logger.error(missing_play)
                    sys.exit()
            case Subject.AVATAR:
                req_av_keys: list[str] = ["avatar", "fighter_banner_info"]
                if not all(k in json_data["pageProps"] for k in req_av_keys):
                    missing_avkey: str = (
                        f"{subject.name} json is missing a required avatar key. Aborting."
                    )
                    logger.error(missing_avkey)
                    self.send_push_alert(missing_avkey)
                    sys.exit()
                req_av_props: list[str] = [
                    "equiped_style",
                    "equipments",
                    "gender",
                    "shisho_characters",
                    "status",
                    "style_list",
                ]
                if not all(k in json_data["pageProps"]["avatar"] for k in req_av_props):
                    missing_avprops: str = (
                        f"{subject.name} json is missing a required avatar properties. Halting."
                    )
                    logger.error(missing_avprops)
                    self.send_push_alert(missing_avprops)
                    sys.exit()
            case (
                Subject.ALL_MATCHES
                | Subject.RANKED_MATCHES
                | Subject.CASUAL_MATCHES
                | Subject.CUSTOM_MATCHES
                | Subject.HUB_MATCHES
            ):
                if "replay_list" not in json_data["pageProps"]:
                    missing_replay: str = (
                        f"{subject.name} json is missing replay_list property. Halting."
                    )
                    logger.error(missing_replay)
                    self.send_push_alert(missing_replay)
                    sys.exit()
                if len(json_data["pageProps"]["replay_list"]) == 0:
                    logger.debug(
                        "Page %d of matches empty. Not downloading.", self.page_number
                    )
                    return False

                if not self._full_battlelog:
                    # Check for dates of matches here

                    matches: list[dict] = json_data["pageProps"]["replay_list"]
                    yesterday_count: int = 0

                    for match in matches:
                        today: datetime = datetime.now().replace(
                            hour=0,
                            minute=0,
                            second=0,
                            microsecond=0,
                            tzinfo=ZoneInfo("America/Los_Angeles"),
                        )
                        match_time = datetime.fromtimestamp(
                            match["uploaded_at"], tz=ZoneInfo("UTC")
                        )
                        match_happened_today: bool = match_time > today

                        if not match_happened_today:
                            yesterday_count += 1

                    if yesterday_count == len(matches) and not self._full_battlelog:
                        logger.debug(
                            "All matches were from yesterday, no need to store."
                        )
                        self._no_more_fetch = True
                        return False
            case _:
                raise NotImplementedError(
                    f"{subject.name} not implemented in _verify_json()"
                )

        return True

    def _store_json(self, json_data: dict, subject: Subject) -> None:
        """Store the json into the cache."""

        # Run sanity check before continuing.
        if not self._verify_json(json_data, subject):
            return

        Path.mkdir(self._cache_dir(subject), parents=True, exist_ok=True)

        with open(self._cache_filename(subject), "w", encoding="utf-8") as f:
            json.dump(json_data, f, ensure_ascii=False, indent=4)

        logger.debug("Stored %s json data into cache.", subject.name)

    def _load_cached_data(self, subject: Subject) -> dict:
        """Fetches the already scraped data."""

        # No stats for the day.
        if not Path.exists(self._cache_dir(subject)):
            logger.debug("Directory for %s missing.", subject.name)
            return {}

        # These specific json is missing.
        if not Path.is_file(self._cache_filename(subject)):
            logger.debug("Missing %s json file!", subject.name)
            return {}

        with open(self._cache_filename(subject), "r", encoding="utf-8") as f:
            return json.loads(f.read())

    def sync_player_overview(self, player_id: str) -> None:
        """Checks and verifies the cache for a player's overview."""
        if not player_id:
            logger.error("[ERROR] player_id required! Halting.")
            sys.exit()

        logger.debug("Syncing overview .json for ID: %s.", player_id)

        self.player_id = player_id
        self._fetch_json(Subject.OVERVIEW)

        logger.info("Overview .json downloaded for player_id: %s.", player_id)

    def sync_club_info(self, club_id: str) -> None:
        """Checks and verifies the cache for a club's stats."""

        logger.debug("Syncing club overview for ID: %s", club_id)

        if not club_id:
            logger.error("[ERROR] club_id required! Halting.")
            sys.exit()

        self.club_id = club_id
        self._fetch_json(Subject.CLUB)

        logger.info("Club stats updated for club_id: %s.", club_id)

    def sync_player_avatar(self, player_id: str) -> None:
        """Checks and verifies the cache for a player's avatar."""

        if not player_id:
            logger.error("[ERROR] player_id required! Halting.")
            sys.exit()

        logger.debug("Syncing player avatar stats for %s", player_id)

        self.player_id = player_id
        self._fetch_json(Subject.AVATAR)

        logger.debug("Avatar updated for player_id: %s", player_id)

    def sync_battlelog(
        self, player_id: str, subject_type: Subject, all_matches: bool = False
    ) -> None:
        """Checks and verifies the cache for the player's battlelog/history (all matches)."""

        if not player_id:
            logger.error("[ERROR] player_id required! Halting.")
            sys.exit()

        if subject_type not in [
            Subject.ALL_MATCHES,
            Subject.RANKED_MATCHES,
            Subject.CASUAL_MATCHES,
            Subject.CUSTOM_MATCHES,
            Subject.HUB_MATCHES,
        ]:

            logger.error(
                "Incorrect match type specified! must be: (ALL_MATCHES, RANKED_MATCHES,\
                      CASUAL_MATCHES, CUSTOM_MATCHES, or HUB_MATCHES)"
            )
            sys.exit()

        self.player_id = player_id

        self._full_battlelog = all_matches
        self.page_number = 1

        battlelog_collection: list[dict] = []

        while self.page_number <= 10:
            logger.debug("Fetching page %d of matches.", self.page_number)
            battlog_dict: dict = self._fetch_json(subject_type)
            battlelog_collection.append(battlog_dict)

            if len(battlog_dict["pageProps"]["replay_list"]) <= 0:
                break

            if self._no_more_fetch and not self._full_battlelog:
                self._no_more_fetch = False
                break

            if self.page_number != 10:
                time.sleep(0.75)  # todo, we dont need to sleep if it's cached data
            self.page_number += 1

        logger.debug("Match history pulled for player_id: %s", player_id)


if __name__ == "__main__":
    if len(sys.argv) == 1:
        print("Mising arguments: (-debug -club -daily -matches -all)")
        print()
        print(
            "-debug:\t\tDownloads everything to /mock folder. (does nothing by itself)"
        )
        print("-club:\t\tDownloads club overview.")
        print("-daily:\t\tDownloads every club member's overview.json for today.")
        print("-matches:\tDownloads every club member's matches for today.")
        print("--all:\tDownloads every club member's matches (all 10 pages).")

    DEBUG = False

    if "-debug" in sys.argv[1:]:
        logger.setLevel(logging.DEBUG)
        DEBUG = True

    cfn_scraper = CFNStatsScraper(datetime.now(), debug_flag=DEBUG)

    if "-club" not in sys.argv[1:] and "-daily" not in sys.argv[1:]:
        sys.exit("Missing -daily or -club, script will do nothing.")

    if "-club" in sys.argv[1:]:
        cfn_scraper.sync_club_info(club_id=cfn_secrets.DEFAULT_CLUB_ID)

    if "-daily" in sys.argv[1:]:
        start_last_update(date=cfn_scraper.date)
        for player in FUNNY_ANIMALS:
            cfn_scraper.sync_player_overview(player_id=player)
            cfn_scraper.sync_player_avatar(player)

            if "-matches" in sys.argv[1:]:
                for match_type in [
                    Subject.ALL_MATCHES,
                    Subject.RANKED_MATCHES,
                    Subject.CASUAL_MATCHES,
                    Subject.CUSTOM_MATCHES,
                    Subject.HUB_MATCHES,
                ]:
                    if "--all" in sys.argv[1:]:
                        cfn_scraper.sync_battlelog(
                            player_id=player,
                            subject_type=match_type,
                            all_matches=True,
                        )
                    else:
                        cfn_scraper.sync_battlelog(
                            player_id=player,
                            subject_type=match_type,
                            all_matches=False,
                        )
        cfn_scraper.send_push_alert(
            f"CFN stats downloaded for {datetime.today().date().strftime('%b %d %Y')}"
        )
        log_last_update(date=cfn_scraper.date, download_complete=True)
