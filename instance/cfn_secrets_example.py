"""Secrets file for cfn_downloader. Replace these with values from your own login
Rename file to 'cfn_secrets.py'.
You will also need the cookie.txt, see cookieread.py.
"""

DEFAULT_PLAYER_ID: str = "3425126856"  # Scrub's CFN
DEFAULT_CLUB_ID: str = "c984cc7ce8cd44b9a209e984a73d0c9e"  # FunnyAnimals

# Notification channel (https://notify.run/)
NOTIFY_CHANNEL: str = "aaabbb333eeewwwDDDD"

# URL_TOKEN:
# Go to CFN profile while logged in and click stats to get the following URL (use Fiddler):
# https://www.streetfighter.com/6/buckler/_next/data/{URL_TOKEN}/en/profile/{PLAYER_ID}/play.json?sid={PLAYER_ID_HERE}

URL_TOKEN: str = "AAABBBCCCDDD"
