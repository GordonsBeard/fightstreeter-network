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

    def __init__(self, date: datetime) -> None:
        self.date: datetime = date
        self._player_id: str = ""
        self._club_id: str = ""
        self.base_cache_dir: Path = Path(
            f"cfn_stats/{str(self.date.year)}/{str(self.date.month)}/{str(self.date.day)}"
        )
        self.url_token: str = cfn_secrets.URL_TOKEN
        self.buckler_id = cfn_secrets.BUCKLER_ID
        self.buckler_r_id = cfn_secrets.BUCKLER_R_ID
        self.buckler_praise_date = cfn_secrets.BUCKLER_PRAISE_DATE

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

        cache_dir: Path = Path(self.base_cache_dir)

        match subject:
            case Subject.OVERVIEW:
                return cache_dir / self.player_id
            case Subject.CLUB:
                return cache_dir / self.club_id
            case _:
                raise NotImplementedError()

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
            case _:
                raise NotImplementedError()

    def _get_req_url(self, subject: Subject) -> str:
        """Returns the request URL for a given subject."""

        url: str = ""

        match subject:
            case Subject.OVERVIEW:
                if not self.player_id:
                    sys.exit("Missing player_id, cannot build request url for data.")

                url = (
                    "https://www.streetfighter.com/6/buckler/_next/data"
                    f"/{self.url_token}/en/profile"
                    f"/{self.player_id}.json?sid={self.player_id}"
                )
            case Subject.CLUB:
                if not self.club_id:
                    sys.exit("Missing club_id, cannot build reqeuest url for data.")

                url = (
                    "https://www.streetfighter.com/6/buckler/_next/data"
                    f"/{self.url_token}/en/club"
                    f"/{self.club_id}.json?clubid={self.club_id}"
                )

        return url

    def _fetch_json(self, subject: Subject) -> dict:
        """Grabs the json object for the request subject. Cache or HTTP hit."""

        cached_data = self._load_cached_data(subject)

        if cached_data:
            print(f"Cached {subject.name} json found.")
            return cached_data

        if self.date.date() < datetime.today().date():
            sys.exit("Cannot request new data from a time before today.")

        cookies: dict[str, str] = {
            "buckler_id": self.buckler_id,
            "buckler_r_id": self.buckler_r_id,
            "buckler_praise_date": self.buckler_praise_date,
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

        match subject:
            case Subject.OVERVIEW:
                req_ov_keys: list[str] = ["fighter_banner_info", "play"]
                if not all(k in json_data["pageProps"] for k in req_ov_keys):
                    sys.exit(
                        f"{subject.name} json is missing a required stats key. Aborting."
                    )

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
                if not all(k in json_data["pageProps"]["play"] for k in req_play_keys):
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

        with open(self._cache_filename(Subject.OVERVIEW), "r", encoding="utf-8") as f:
            return json.loads(f.read())

    def sync_player_stats(self, player_id: str) -> None:
        """Checks and verifies the cache for a player's stats."""

        if not player_id:
            sys.exit("player_id required!")

        self.player_id = player_id
        player_overview_data: dict = self._fetch_json(Subject.OVERVIEW)

        player_name: str = player_overview_data["pageProps"]["fighter_banner_info"][
            "personal_info"
        ]["fighter_id"]

        print(f"{player_name} stats updated for {self.date}")

    def sync_club_stats(self, club_id: str) -> None:
        """Checks and verifies the cache for a club's stats."""

        if not club_id:
            sys.exit("club_id required!")

        self.club_id = club_id
        club_data: dict = self._fetch_json(Subject.CLUB)

        club_name = club_data["pageProps"]["circle_base_info"]["name"]

        print(f"{club_name} stats updated for {self.date}")


if __name__ == "__main__":
    cfn_scraper = CFNStatsScraper(datetime.now())
    cfn_scraper.sync_player_stats(player_id=cfn_secrets.DEFAULT_PLAYER_ID)

    cfn_scraper.sync_club_stats(club_id=cfn_secrets.DEFAULT_CLUB_ID)
