"""Module providing for the scraping of CFN for player stats"""

import requests
import cfn_secrets

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
        'Host': 'www.streetfighter.com',
        'Pragma': 'no-cache',
        'Referer': 'https://www.streetfighter.com/6/buckler/profile/4249556471/play',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0)'\
                'Gecko/20100101 Firefox/120.0'
    }

    def __init__(self, **kwargs):
        self.player_id:str = cfn_secrets.DEFAULT_PLAYER_ID \
            if 'player_id' not in kwargs \
                else kwargs['player_id']

    def get_player_stats(self) -> None:
        """Grabs the basic profile data for the user."""

        response = requests.get(
            self._PLAYER_STATS_URL.format(
                url_token=cfn_secrets.URL_TOKEN,
                player_id=self.player_id),
            timeout=5,
            headers=self._headers,
            cookies=self._cookies
            )

        profile_json_data = response.json()

        player_character_winrates = profile_json_data['pageProps']['play']['character_win_rates']

        for player in player_character_winrates:
            if player['character_alpha'] == 'DHALSIM':
                stats = player

        print(f"Scrub has used {stats['character_name']} {stats['battle_count']} times this phase.")

if __name__ == '__main__':
    cfn_scraper = CFNStatsScraper()
    cfn_scraper.get_player_stats()
