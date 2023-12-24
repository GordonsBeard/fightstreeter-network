"""Module providing for the scraping of CFN for player stats"""

import json
import sys
from datetime import datetime
from pathlib import Path

import requests

import cfn_secrets


class CFNStatsScraper:
    """Object that grabs the data from the website"""

    _HOSTNAME: str = "www.streetfighter.com"
    _CFN_ROOT: str = f"https://{_HOSTNAME}/6/buckler/"
    _PROFILE_URL: str = _CFN_ROOT + "en/profile/{player_id}"
    _PLAYER_PROFILE_URL: str = (
        _CFN_ROOT + "/_next/data/{url_token}/en"
        "/profile/{player_id}.json?sid={player_id}"
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

    def __init__(self, **kwargs) -> None:
        self.player_id: str = (
            kwargs["player_id"]
            if "player_id" in kwargs
            else cfn_secrets.DEFAULT_PLAYER_ID
        )
        self.date: datetime = kwargs["date"] if "date" in kwargs else datetime.now()

    @property
    def profile_cache_dir(self) -> Path:
        """Returns the path for the player's profile json cache."""

        return Path(
            f"player_stats/{str(self.date.year)}/{str(self.date.month)}/{str(self.date.day)}/{self.player_id}"
        )

    @property
    def profile_cache_filename(self):
        """Returns the filename for the player's cached profile data."""

        return Path(self.profile_cache_dir / f"{self.player_id}_profile.json")

    def _fetch_player_profile_json(self) -> dict:
        """Grabs the basic profile data for the user."""

        cached_data = self._load_cached_data()

        if cached_data:
            print("Cached data found.")
            return cached_data

        if self.date.date() < datetime.today().date():
            sys.exit("Cannot request new data from a time before today.")

        print("Making request for new data.")
        response: requests.Response = requests.get(
            self._PLAYER_PROFILE_URL.format(
                url_token=cfn_secrets.URL_TOKEN, player_id=self.player_id
            ),
            timeout=5,
            headers=self._headers,
            cookies=self._cookies,
        )

        if response.status_code != 200:
            sys.exit(f"Bad request! Status code: {response.status_code}")

        # This is the full json file
        profile_json_data: dict = response.json()

        # Store it for cache purposes
        self._store_player_profile(profile_json_data)

        return profile_json_data

    def _store_player_profile(self, player_stats: dict) -> None:
        """Store the player profile into the cache."""

        with open(self.profile_cache_filename, "w", encoding="utf-8") as f:
            json.dump(player_stats, f, ensure_ascii=False, indent=4)

        print("Stored player data.")

    def _load_cached_data(self) -> dict:
        """Fetch the already scraped json data."""

        if not Path.exists(self.profile_cache_dir):
            print(f"Player stats directory {self.profile_cache_dir} missing.")

            if self.date.date() < datetime.today().date():
                print("Date requested is before today. Cannot build cache.")
                return {}

            print("Creating folder.")
            Path.mkdir(self.profile_cache_dir, parents=True, exist_ok=True)
            return {}  # missing the directory, we won't have the cache

        if not Path.is_file(self.profile_cache_filename):
            print("Missing player_data.json file!")
            return {}  # we have the stats for the day, but not for this user

        with open(self.profile_cache_filename, "r", encoding="utf-8") as f:
            return json.loads(f.read())  # we got the goods

    def do_shit(self) -> None:
        """Display some stuff to see if the code is working."""

        player_profile_json: dict = self._fetch_player_profile_json()

        player_name: str = player_profile_json["pageProps"]["fighter_banner_info"][
            "personal_info"
        ]["fighter_id"]

        player_character_winrates: dict = player_profile_json["pageProps"]["play"][
            "character_win_rates"
        ]

        player_profile: dict = {}

        chars = ["DHALSIM", "ZANGIEF", "DEE JAY"]

        for player in player_character_winrates:
            if player["character_alpha"] in chars:
                player_profile = player
                print(
                    f"{player_name} has used {player_profile['character_name']} "
                    f"{player_profile['battle_count']} times this phase."
                )


if __name__ == "__main__":
    CFN_ID: str = cfn_secrets.DEFAULT_PLAYER_ID
    date: datetime = datetime.today()

    args = sys.argv[1:]
    if len(args) == 2:
        CFN_ID = args[0]
        raw_date: str = args[1]
        date = datetime.strptime(raw_date, "%Y-%m-%d")

    cfn_scraper = CFNStatsScraper(player_id=CFN_ID, date=date)
    cfn_scraper.do_shit()
