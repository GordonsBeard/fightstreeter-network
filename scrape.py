"""Module providing for the scraping of CFN for player stats"""

import requests

# user id values
url_token:str = '7R1j0S8w9k0X3T3Db5_0h'
buckler_id:str = 'okH4OHGYRUDiMTIzLWrchv2YjwESkOusG3HsOtAHw2CMXkZJFGcHPz4BEYssy1QR'
buckler_r_id:str = ''
buckler_praise_date:str = '1703310838092'

player_id:str = '3425126856' #scrub

cookies:dict[str, str] = {
    'buckler_id' : buckler_id, 
    'buckler_r_id' : buckler_r_id, 
    'buckler_praise_date': buckler_praise_date
}

headers:dict[str, str] = {
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
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0'
}

url:str = f'https://www.streetfighter.com/6/buckler/_next/data/{url_token}/en/profile/{player_id}.json?sid={player_id}'

response = requests.get(
    url,
    timeout=5,
    headers=headers,
    cookies=cookies
    )

profile_json_data = response.json()

player_character_winrates = profile_json_data['pageProps']['play']['character_win_rates']

for player in player_character_winrates:
    if player['character_alpha'] == 'DHALSIM':
        stats = player

print(f"Scrub has used {stats['character_name']} {stats['battle_count']} times this phase.")


# TODO
# https://github.com/Xjph/CFNScrape/tree/master/CFNScrape
