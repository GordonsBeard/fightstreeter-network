"""Module providing for the scraping of CFN for player stats"""

import json
import sys
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path

import requests

import cfn_secrets


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
    _buckler_id = cfn_secrets.BUCKLER_ID
    _buckler_r_id = cfn_secrets.BUCKLER_R_ID
    _buckler_praise_date = cfn_secrets.BUCKLER_PRAISE_DATE

    _charid_map: dict[int, str] = {
        1: "",
        2: "",
        3: "",
        4: "",
        5: "",
        6: "",
        7: "",
        8: "Dhalsim",
        9: "",
        10: "",
        11: "",
        12: "",
        13: "",
        14: "",
        15: "",
        16: "",
        17: "",
        18: "",
        19: "",
        20: "",
        21: "",
        22: "",
        23: "",
    }

    def __init__(self, date: datetime) -> None:
        self.date: datetime = date
        self._player_id: str = ""
        self._club_id: str = ""
        self.base_cache_dir: Path = Path(
            f"cfn_stats/{str(self.date.year)}/{str(self.date.month)}/{str(self.date.day)}"
        )

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

    def _cache_dir(self, subject: Subject) -> Path:
        """Returns the path for the cached json."""

        match subject:
            case Subject.OVERVIEW | Subject.STATS | Subject.AVATAR:
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
            case _:
                raise NotImplementedError(
                    f"{subject.name} not implemented in _cache_filename()"
                )

    def _get_req_url(self, subject: Subject) -> str:
        """Returns the request URL for a given subject."""
        match subject:
            case Subject.OVERVIEW:
                if not self.player_id:
                    sys.exit("Missing player_id, cannot build request url for data.")

                return (
                    "https://www.streetfighter.com/6/buckler/_next/data"
                    f"/{self._url_token}/en/profile"
                    f"/{self.player_id}.json?sid={self.player_id}"
                )
            case Subject.CLUB:
                if not self.club_id:
                    sys.exit("Missing club_id, cannot build reqeuest url for data.")

                return (
                    "https://www.streetfighter.com/6/buckler/_next/data"
                    f"/{self._url_token}/en/club"
                    f"/{self.club_id}.json?clubid={self.club_id}"
                )
            case Subject.STATS:
                if not self.player_id:
                    sys.exit("Missing player_id, cannot build request url for data.")

                return (
                    "https://www.streetfighter.com/6/buckler/_next/data"
                    f"/{self._url_token}/en/profile"
                    f"/{self.player_id}/play.json?sid={self.player_id}"
                )
            case Subject.AVATAR:
                if not self.player_id:
                    sys.exit("Missing player_id, cannot build request url for data.")

                return (
                    "https://www.streetfighter.com/6/buckler/_next/data"
                    f"/{self._url_token}/en/profile"
                    f"/{self.player_id}/avatar.json?sid={self.player_id}"
                )
            case _:
                raise NotImplementedError(
                    f"{subject.name} not implemented in _get_req_url()"
                )

    def _fetch_json(self, subject: Subject) -> dict:
        """Grabs the json object for the request subject. Cache or HTTP hit."""

        cached_data = self._load_cached_data(subject)

        if cached_data:
            return cached_data

        if self.date.date() < datetime.today().date():
            sys.exit("Cannot request new data from a time before today.")

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

        print("Making request for new data.")

        response: requests.Response = requests.get(
            self._get_req_url(subject),
            timeout=5,
            headers=headers,
            cookies=cookies,
        )

        if response.status_code != 200:
            if response.status_code == 403:
                print("You probably need to log in again and update the secrets.")
            sys.exit(f"Bad request! Status code: {response.status_code}")

        json_data: dict = response.json()

        # Store it for cache purposes
        self._store_json(json_data, subject)

        return json_data

    def _verify_json(self, json_data: dict, subject: Subject) -> None:
        """Does sanity checks on the keys expected in the json data."""

        if not json_data:
            sys.exit(f"{subject.name} json is empty. Aborting.")

        if "pageProps" not in json_data:
            sys.exit(
                f"{subject.name} json is missing root 'pageProps' element. Aborting."
            )

        req_profile_keys: list[str] = ["fighter_banner_info", "play"]

        match subject:
            case Subject.OVERVIEW:
                if not all(k in json_data["pageProps"] for k in req_profile_keys):
                    sys.exit(
                        f"{subject.name} json is missing a required stats key. Aborting."
                    )
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
                    sys.exit(
                        f"{subject.name} data is incomplete, missing keys in 'play' "
                        "section. Aborting."
                    )
            case Subject.CLUB:
                req_club_keys: list[str] = [
                    "circle_base_info",
                    "circle_member_list",
                    "circle_timeline_list",
                ]
                if not all(k in json_data["pageProps"] for k in req_club_keys):
                    sys.exit(
                        f"{subject.name} json is missing a required stats key. Aborting."
                    )
            case Subject.STATS:
                if not all(k in json_data["pageProps"] for k in req_profile_keys):
                    sys.exit(
                        f"{subject.name} json is missing a required stats key. Aborting."
                    )
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
                    sys.exit(
                        f"{subject.name} json is missing a required play key. Aborting."
                    )
            case Subject.AVATAR:
                req_av_keys: list[str] = ["avatar", "fighter_banner_info"]
                if not all(k in json_data["pageProps"] for k in req_av_keys):
                    sys.exit(
                        f"{subject.name} json is missing a required avatar key. Aborting."
                    )
                req_av_props: list[str] = [
                    "equiped_style",
                    "equipments",
                    "gender",
                    "shisho_characters",
                    "status",
                    "style_list",
                ]
                if not all(k in json_data["pageProps"]["avatar"] for k in req_av_props):
                    sys.exit(
                        f"{subject.name} json is missing a required avatar properties. "
                        "Aborting."
                    )
            case _:
                raise NotImplementedError(
                    f"{subject.name} not implemented in _verify_json()"
                )

    def _store_json(self, json_data: dict, subject: Subject) -> None:
        """Store the json into the cache."""

        # Run sanity check before continuing.
        self._verify_json(json_data, subject)

        Path.mkdir(self._cache_dir(subject), parents=True, exist_ok=True)

        with open(self._cache_filename(subject), "w", encoding="utf-8") as f:
            json.dump(json_data, f, ensure_ascii=False, indent=4)

        print(f"Stored {subject.name} json data into cache.")

    def _load_cached_data(self, subject: Subject) -> dict:
        """Fetches the already scraped data."""

        # No stats for the day.
        if not Path.exists(self._cache_dir(subject)):
            print(f"Directory for {subject.name} missing.")
            return {}

        # These specific json is missing.
        if not Path.is_file(self._cache_filename(subject)):
            print(f"Missing {subject.name} json file!")
            return {}

        with open(self._cache_filename(subject), "r", encoding="utf-8") as f:
            return json.loads(f.read())

    def sync_player_overview(self, player_id: str) -> None:
        """Checks and verifies the cache for a player's overview."""

        print(f"Syncing player overview for ID: {player_id}")
        if not player_id:
            sys.exit("player_id required!")

        self.player_id = player_id
        player_overview_data: dict = self._fetch_json(Subject.OVERVIEW)

        player_name: dict = player_overview_data["pageProps"]["fighter_banner_info"][
            "personal_info"
        ]["fighter_id"]

        current_char_id: int = player_overview_data["pageProps"]["fighter_banner_info"][
            "favorite_character_id"
        ]

        current_char: str = self._charid_map[current_char_id]

        current_rank: str = player_overview_data["pageProps"]["fighter_banner_info"][
            "favorite_character_league_info"
        ]["league_rank_info"]["league_rank_name"]

        current_lp: str = player_overview_data["pageProps"]["fighter_banner_info"][
            "favorite_character_league_info"
        ]["league_point"]

        print(
            f"{player_name} overview updated for {self.date}"
            "\n"
            f"Current character: {current_char} ({current_rank} {current_lp} LP)."
        )
        print()

    def sync_club_info(self, club_id: str) -> None:
        """Checks and verifies the cache for a club's stats."""

        print(f"Syncing club overview for ID: {club_id}")

        if not club_id:
            sys.exit("club_id required!")

        self.club_id = club_id
        club_data: dict = self._fetch_json(Subject.CLUB)

        club_name = club_data["pageProps"]["circle_base_info"]["name"]

        print(f"{club_name} stats updated for {self.date}")
        print()

    def sync_player_stats(self, player_id: str) -> None:
        """Checks and verifies the cache for a player's stats."""

        if not player_id:
            sys.exit("player_id required!")

        print(f"Syncing player stats for ID: {player_id}")

        self.player_id = player_id
        stats_data: dict = self._fetch_json(Subject.STATS)

        playtimes = stats_data["pageProps"]["play"]["base_info"][
            "content_play_time_list"
        ]

        [extreme_playtime] = [
            timedelta(seconds=x["play_time"])
            for x in playtimes
            if x["content_type_name"] == "Extreme"
        ]

        player_name: str = stats_data["pageProps"]["fighter_banner_info"][
            "personal_info"
        ]["fighter_id"]

        print(f"{player_name} has played {extreme_playtime} of Extreme battles.")
        print(f"{player_name} stats updated for {self.date}")
        print()

    def sync_player_avatar(self, player_id: str) -> None:
        """Checks and verifies the cache for a player's avatar."""

        if not player_id:
            sys.exit("player_id required!")

        print(f"Syncing player avatar stats for {player_id}")

        self.player_id = player_id
        avatar_data: dict = self._fetch_json(Subject.AVATAR)

        avatar_level: str = avatar_data["pageProps"]["avatar"]["status"]["level"]

        player_name: str = avatar_data["pageProps"]["fighter_banner_info"][
            "personal_info"
        ]["fighter_id"]

        print(f"{player_name}'s level {avatar_level} avatar updated for {self.date}")
        print()


if __name__ == "__main__":
    cfn_scraper = CFNStatsScraper(datetime.now())
    print()
    cfn_scraper.sync_player_overview(player_id=cfn_secrets.DEFAULT_PLAYER_ID)
    cfn_scraper.sync_club_info(club_id=cfn_secrets.DEFAULT_CLUB_ID)
    cfn_scraper.sync_player_stats(player_id=cfn_secrets.DEFAULT_PLAYER_ID)
    cfn_scraper.sync_player_avatar(player_id=cfn_secrets.DEFAULT_PLAYER_ID)
