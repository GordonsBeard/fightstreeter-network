"""Secrets file for CFN Stats Scraper. Replace these with values from your own login
   Rename file to 'cfn_secrets.py'.
   You will also need the cookie.txt, see cookieread.py, will merge this later.
"""

DEFAULT_PLAYER_ID: str = "3425126856"  # Scrub's CFN
DEFAULT_CLUB_ID: str = "c984cc7ce8cd44b9a209e984a73d0c9e"  # FunnyAnimals

# URL_TOKEN:
# Go to profile and click "stats" to get the following URL (use Fiddler):
# https://www.streetfighter.com/6/buckler/_next/data/{URL_TOKEN_HERE}/en/profile/{PLAYER_ID_HERE}/play.json?sid={PLAYER_ID_HERE}

URL_TOKEN: str = "AAABBBCCCDDD"

# Notification channel (https://notify.run/)
NOTIFY_CHANNEL: str = "aaabbb333eeewwwDDDD"
