# cfn stats grabber

this is multiple projects:
- Scraper
    - ONLY downloads the raw .json files
- Parser/Inserter (load the cache)
    - reads the json
    - puts into database
- Website (reads the database)

these scripts download the cfn street fighter 6 data in .json format. later it might not
save the entire thing and just keep the important bits.

cfn only stores the last 100 matches so if you fight a lot: those matches are known only
to you and the aether.

this readme is for myself (older, more forgetful) or someone else completely (you, attractive)

## run the daily stats

1. get the *cfn-secrets.py* tokens filled out
2. python **./scraper.py** (gets the .json downloaded for today)
3. python **./parseinsert.py** (inserts the info to the database)
    a. this also updates the club userlist

## notes that complicate it

* if you're not the leader of the club you can't get the memberlist
* no automation for getting the secrets