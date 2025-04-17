"""This file implements the cfnscraper and cfnparser functions so the backend can access their results."""

import re
import sys
from datetime import datetime

from cfnscraper.scrape import CFNStatsScraper, Subject
from constants import FUNNY_ANIMALS
from instance import cfn_secrets
from last_updated import log_last_update, start_last_update


def parse_cookie_file(cookies_file: str):
    """Parse a cookies.txt file and return a dictionary of key value pairs compatible with requests."""

    cookie_dict: dict[str, str] = {}
    with open(cookies_file, "r", encoding="utf-8") as fp:
        for line in fp:
            if not re.match(r"^\#", line) and line != "\n":
                line_fields = line.strip().split("\t")
                cookie_dict[line_fields[5]] = line_fields[6]
    return cookie_dict


if __name__ == "__main__":
    cookies = parse_cookie_file("instance/cookies.txt")

    BUCKLER_ID: str = cookies["buckler_id"]
    BUCKLER_R_ID: str = cookies["buckler_r_id"]
    BUCKLER_PRAISE_DATE: str = cookies["buckler_praise_date"]

    if len(sys.argv) == 1:
        print("Mising arguments: -daily [-debug -all]")
        print()
        print(
            "-debug:\t\tDownloads everything to /mock folder. (does nothing by itself)"
        )
        print(
            "-daily:\t\tDownloads every club member's overview.json & matches for today."
        )
        print("-all:\tDownloads every club member's matches (all 10 pages).")

    DEBUG = False

    if "-debug" in sys.argv[1:]:
        DEBUG = True

    cfn_scraper = CFNStatsScraper(
        datetime.now(),
        DEBUG,
        cfn_secrets.NOTIFY_CHANNEL,
        cfn_secrets.URL_TOKEN,
        BUCKLER_ID,
        BUCKLER_R_ID,
        BUCKLER_PRAISE_DATE,
        cfn_secrets.DEFAULT_PLAYER_ID,
    )

    if "-daily" not in sys.argv[1:]:
        sys.exit("Missing -daily, script will do nothing. Exiting.")

    if "-daily" in sys.argv[1:]:
        start_last_update(date=cfn_scraper.date)
        cfn_scraper.sync_club_info(club_id=cfn_secrets.DEFAULT_CLUB_ID)
        for player in FUNNY_ANIMALS:
            cfn_scraper.sync_player_overview(player_id=player)
            cfn_scraper.sync_player_avatar(player)

            for match_type in [
                Subject.ALL_MATCHES,
                Subject.RANKED_MATCHES,
                Subject.CASUAL_MATCHES,
                Subject.CUSTOM_MATCHES,
                Subject.HUB_MATCHES,
            ]:
                if "-all" in sys.argv[1:]:
                    cfn_scraper.sync_battlelog(
                        player_id=player,
                        subject_type=match_type,
                        all_matches=True,
                    )
                else:
                    cfn_scraper.sync_battlelog(
                        player_id=player,
                        subject_type=match_type,
                        all_matches=False,
                    )
        cfn_scraper.send_push_alert(
            f"CFN stats downloaded for {datetime.today().date().strftime('%b %d %Y')}"
        )
        log_last_update(date=cfn_scraper.date, download_complete=True)
