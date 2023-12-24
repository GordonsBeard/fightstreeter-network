"""Module providing for the scraping of CFN for player stats"""

import cfn_secrets
import json
import os.path
import requests
import sys

class CFNStatsScraper:
    """Object that grabs the data from the website"""

    _HOSTNAME:str = 'www.streetfighter.com'
    _CFN_ROOT:str = f'https://{_HOSTNAME}/6/buckler/'
    _PROFILE_URL:str = _CFN_ROOT + 'en/profile/{player_id}'
    _PLAYER_STATS_URL:str = _CFN_ROOT + '/_next/data/{url_token}/en'\
        '/profile/{player_id}.json?sid={player_id}'

    _cookies:dict[str, str] = {
        'buckler_id' : cfn_secrets.BUCKLER_ID,
        'buckler_r_id' : cfn_secrets.BUCKLER_R_ID,
        'buckler_praise_date': cfn_secrets.BUCKLER_PRAISE_DATE
    }

    _headers:dict[str, str] = {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en,q=0.9',
        'Cache-Content': 'no-cache',
        'Connection': 'keep-alive',
        'Host': _HOSTNAME,
        'Pragma': 'no-cache',
        'Referer': 'https://www.streetfighter.com/6/buckler/profile/'\
            f'{cfn_secrets.DEFAULT_PLAYER_ID}/play',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0)'\
                'Gecko/20100101 Firefox/120.0'
    }

    def __init__(self, **kwargs) -> None:
        self.player_id:str = cfn_secrets.DEFAULT_PLAYER_ID \
            if 'player_id' not in kwargs \
                else kwargs['player_id']

    def _fetch_player_stats(self) -> dict:
        """Grabs the basic profile data for the user."""

        if self._check_if_stats_exist():
            print("Cached data found.")
            return self._load_cached_data()

        print("Making request for new data!")

        response: requests.Response = requests.get(
            self._PLAYER_STATS_URL.format(
                url_token=cfn_secrets.URL_TOKEN,
                player_id=self.player_id),
            timeout=5,
            headers=self._headers,
            cookies=self._cookies
            )

        if response.status_code != 200:
            sys.exit(f'Bad request! Status code: {response.status_code}')

        # This is the full json file
        profile_json_data:dict = response.json()

        # Store it for cache purposes
        self._store_player_stats(profile_json_data)

        return profile_json_data

    def _check_if_stats_exist(self) -> bool:
        """Returns true if the requested player's stats for this date exists."""

        if not os.path.exists('player_stats'):
            print("Player stats directory 'player_stats' missing!")
            return False

        if not os.path.isfile(os.path.join('player_stats', 'player_data.json')):
            print("Missing player_data.json file!")
            return False

        return True

    def _store_player_stats(self, player_stats:dict):
        """Store the json object with logical names."""

        with open(os.path.join('player_stats', 'player_data.json'), 'w', encoding='utf-8') as f:
            json.dump(player_stats, f, ensure_ascii=False, indent=4)

        print("Stored player data.")



    def _load_cached_data(self) -> dict:
        """Fetch the already scraped json data."""

        with open(os.path.join('player_stats', 'player_data.json'), encoding='utf-8') as f:
            return json.loads(f.read())


    def get_player_stats(self) -> None:
        """Display some stats to see if the code is working."""

        player_stats:dict = self._fetch_player_stats()

        player_character_winrates:dict = \
            player_stats['pageProps']['play']['character_win_rates']

        stats:dict = {}

        for player in player_character_winrates:
            if player['character_alpha'] == 'DHALSIM':
                stats = player

        print(f"Scrub has used {stats['character_name']} {stats['battle_count']} times this phase.")

if __name__ == '__main__':
    cfn_scraper = CFNStatsScraper()
    cfn_scraper.get_player_stats()
