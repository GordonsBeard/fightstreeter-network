"""Module providing for the scraping of CFN for player stats"""

import json
import sys
from datetime import datetime
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
    HISTORY = 5


class CFNStatsScraper:
    """Object that grabs the data from the website"""

    _HOSTNAME: str = "www.streetfighter.com"
    _CFN_ROOT: str = f"https://{_HOSTNAME}/6/buckler/"
    _PROFILE_URL: str = _CFN_ROOT + "en/profile/{player_id}"
    _PLAYER_OVERVIEW_URL: str = (
        _CFN_ROOT + "/_next/data/{url_token}/en"
        "/profile/{player_id}.json?sid={player_id}"
    )
    _CLUB_URL: str = (
        _CFN_ROOT + "/_next/data/{url_token}/en" "/club/{club_id}.json?sid={club_id}"
    )

    _cookies: dict[str, str] = {
        "buckler_id": cfn_secrets.BUCKLER_ID,
        "buckler_r_id": cfn_secrets.BUCKLER_R_ID,
        "buckler_praise_date": cfn_secrets.BUCKLER_PRAISE_DATE,
    }

    _headers: dict[str, str] = {
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "en-US,en,q=0.9",
        "Cache-Content": "no-cache",
        "Connection": "keep-alive",
        "Host": _HOSTNAME,
        "Pragma": "no-cache",
        "Referer": f"{_CFN_ROOT}profile/{cfn_secrets.DEFAULT_PLAYER_ID}/play",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
    }

    def __init__(self, date: datetime) -> None:
        self._player_id: str = ""
        self._club_id: str = ""
        self.date: datetime = date
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
            case Subject.OVERVIEW:
                return Path(self.base_cache_dir / self.player_id)
            case Subject.CLUB:
                return Path(self.base_cache_dir / self.club_id)

        return Path()  # todo this isn't good

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

        return Path()  # todo this isn't good

    @property
    def overview_cache_dir(self) -> Path:
        """Returns the path for the player's overview json cache."""

        return self._cache_dir(Subject.OVERVIEW)

    @property
    def overview_cache_filename(self):
        """Returns the filename for the player's cached overview data."""

        return self._cache_filename(Subject.OVERVIEW)

    @property
    def club_cache_dir(self) -> Path:
        """Returns the path for the club's json cache."""

        return self._cache_dir(Subject.CLUB)

    @property
    def club_cache_filename(self):
        """Returns the filename for the club's cached data."""

        return self._cache_filename(Subject.CLUB)

    def _fetch_player_overview_json(self) -> dict:
        """Grabs the user overview data."""

        cached_data = self._load_profile_cached_data()

        if cached_data:
            print("Cached profile overview data found.")
            return cached_data

        if self.date.date() < datetime.today().date():
            sys.exit("Cannot request new data from a time before today.")

        print("Making request for new data.")
        response: requests.Response = requests.get(
            self._PLAYER_OVERVIEW_URL.format(
                url_token=cfn_secrets.URL_TOKEN, player_id=self.player_id
            ),
            timeout=5,
            headers=self._headers,
            cookies=self._cookies,
        )

        if response.status_code != 200:
            sys.exit(f"Bad request! Status code: {response.status_code}")

        overview_json_data: dict = response.json()

        # Store it for cache purposes
        self._store_player_overview(overview_json_data)

        return overview_json_data

    def _fetch_club_json(self) -> dict:
        """Grabs the club's data."""

        cached_data = self._load_club_cached_data()

        if cached_data:
            print("Cached club data found.")
            return cached_data

        if self.date.date() < datetime.today().date():
            sys.exit("Cannot request new data from a time before today.")

        print("Making request for new club data.")
        response: requests.Response = requests.get(
            self._CLUB_URL.format(
                url_token=cfn_secrets.URL_TOKEN, club_id=self.club_id
            ),
            timeout=5,
            headers=self._headers,
            cookies=self._cookies,
        )

        if response.status_code != 200:
            sys.exit(f"Bad request! Status code: {response.status_code}")

        club_json_data: dict = response.json()

        # Store it for cache purposes
        self._store_club_data(club_json_data)

        return club_json_data

    def _verify_overview_json(self, overview_json_data: dict) -> None:
        """Does some sanity checks on the keys expected for overview data."""

        if "pageProps" not in overview_json_data:
            sys.exit("Data is missing root 'pageProps' element. Aborting.")

        req_keys = ("fighter_banner_info", "play")
        if not all(k in overview_json_data["pageProps"] for k in req_keys):
            sys.exit("Data is missing a required stats key. Aborting.")

        req_play_keys: list[str] = [
            "base_info",
            "battle_stats",
            "character_league_infos",
            "character_play_point_infos",
            "character_win_rates",
            "character_win_rates_by_rival_character",
            "current_season_id",
            "season_ids",
        ]
        if not all(k in overview_json_data["pageProps"]["play"] for k in req_play_keys):
            sys.exit("Play data is incomplete, missing key. Aborting.")

    def _store_player_overview(self, player_stats: dict) -> None:
        """Store the player overview into the cache."""

        # Run sanity check before continuing.
        self._verify_overview_json(player_stats)

        with open(self.overview_cache_filename, "w", encoding="utf-8") as f:
            json.dump(player_stats, f, ensure_ascii=False, indent=4)

        print("Stored player data.")

    def _store_club_data(self, club_stats: dict) -> None:
        """Store the club stats into the cache."""

        # Run sanity check before continuing.
        # todo
        # self._verify_overview_json(club_stats)

        with open(self.club_cache_filename, "w", encoding="utf-8") as f:
            json.dump(club_stats, f, ensure_ascii=False, indent=4)

        print("Stored club data.")

    def _load_profile_cached_data(self) -> dict:
        """Fetch the already scraped player overview json."""

        if not Path.exists(self.overview_cache_dir):
            print(f"Player stats directory {self.overview_cache_dir} missing.")

            if self.date.date() < datetime.today().date():
                print("Date requested is before today. Cannot build cache.")
                return {}

            print("Creating user folder.")
            Path.mkdir(self.overview_cache_dir, parents=True, exist_ok=True)
            return {}  # missing the directory, we won't have the cache

        if not Path.is_file(self.overview_cache_filename):
            print("Missing <player_id>_overview.json file!")
            return {}  # we have the stats for the day, but not for this user

        with open(self.overview_cache_filename, "r", encoding="utf-8") as f:
            return json.loads(f.read())  # we got the goods

    def _load_club_cached_data(self) -> dict:
        """Fetch the already scraped group json."""

        if not Path.exists(self.club_cache_dir):
            print(f"Club stats directory {self.club_cache_dir} missing.")

            if self.date.date() < datetime.today().date():
                print("Date requested is before today. Cannot build cache.")
                return {}

            print("Creating club folder.")
            Path.mkdir(self.club_cache_dir, parents=True, exist_ok=True)
            return {}  # missing the directory, we won't have the cache

        if not Path.is_file(self.club_cache_filename):
            print("Missing <club_id>.json file!")
            return {}  # we have the stats for the day, but not for this club

        with open(self.club_cache_filename, "r", encoding="utf-8") as f:
            return json.loads(f.read())  # we got the goods

    def sync_player_stats(self, player_id: str) -> None:
        """Checks and verifies the cache for a player's stats."""

        if not player_id:
            sys.exit("player_id required!")

        self.player_id = player_id
        player_overview_data: dict = self._fetch_player_overview_json()

        player_name: str = player_overview_data["pageProps"]["fighter_banner_info"][
            "personal_info"
        ]["fighter_id"]

        print(f"{player_name} stats updated for {self.date}")

    def sync_club_stats(self, club_id: str) -> None:
        """Checks and verifies the cache for a club's stats."""

        if not club_id:
            sys.exit("club_id required!")

        self.club_id = club_id
        club_data: dict = self._fetch_club_json()

        club_name = club_data["pageProps"]["circle_base_info"]["name"]

        print(f"{club_name} stats updated for {self.date}")


if __name__ == "__main__":
    cfn_scraper = CFNStatsScraper(datetime.now())
    cfn_scraper.sync_player_stats(player_id=cfn_secrets.DEFAULT_PLAYER_ID)

    cfn_scraper.sync_club_stats(club_id=cfn_secrets.DEFAULT_CLUB_ID)
