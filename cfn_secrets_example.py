"""Secrets file for CFN Stats Scraper. Replace these with values from your own login
   Rename file to 'cfn_secrets.py'
"""

DEFAULT_PLAYER_ID:str = '3425126856' # Scrub's CFN
DEFAULT_CLUB_ID:str = 'c984cc7ce8cd44b9a209e984a73d0c9e' # FunnyAnimals

# URL_TOKEN:
# Go to profile and click "stats" to get the following URL (use Fiddler):
# https://www.streetfighter.com/6/buckler/_next/data/{URL_TOKEN_HERE}/en/profile/{PLAYER_ID_HERE}/play.json?sid={PLAYER_ID_HERE}

URL_TOKEN:str = 'AAABBBCCCDDD'

# BUCKLER_ID & BUCKLER_R_ID & PRAISE_DATE
# You get this from the cookie the website stores. (use Fiddler)
# Look for the "buckler_id" and "buckler_praise_date" values.

BUCKLER_ID:str = 'AAABBBDDDCCCEEEFFFGGGHHHIIIJJJKKKLLLMMM'
BUCKLER_R_ID:str = 'aaaaa-bbbbb-ccccc-dddd'
BUCKLER_PRAISE_DATE:str = '111222333444'
