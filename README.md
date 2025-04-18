# fightstreeter-network

This repo represents multiple projects coming together like a turduken of sorts.

- cfnscraper
    - Utility program that handles querying and downloading the JSON response from CFN's website.
    - All .json files are downloaded and stored in their raw format.
- cfnparser
    - Utility program that reads the .json files and builds a sqlite database.
- fightstreetapi
    - Flask backend serving up an API of compiled stats.
- fighstreetreact
    - React frontend to display contents of API.

Limitations:
- Currently saving the date as no more granular than just the day. Might move to timestamps later, not worth it really.
- CFN only shows 100 matches at a time. If you fight more than this, cfnscraper will miss these.
- cfnscraper can only get Club members if you are the Club owner.

this readme is for myself (older, more forgetful) or someone else completely (you, attractive)

## run the daily stats

1. get the *instance/cfn-secrets.py* tokens filled out
2. update *instance/cookies.txt* with latest CFN login cookies file
3. **./control_center.py -daily [-debug -all]** (this runs the scraper and parser)