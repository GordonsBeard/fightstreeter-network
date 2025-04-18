"""This file implements the cfnscraper and cfnparser functions so the backend can access their results."""

import re
import sqlite3
import sys
from datetime import datetime

from cfnparser.cfnparser import CFNStatsParser
from cfnscraper.cfnscraper import CFNStatsScraper, Subject
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


def init_db():
    """DELETES and initializes new databases."""
    db = sqlite3.connect("instance/cfn-stats.db", detect_types=sqlite3.PARSE_DECLTYPES)
    with open("schema.sql", encoding="utf-8") as f:
        db.executescript(f.read())


if __name__ == "__main__":
    cookies = parse_cookie_file("instance/cookies.txt")

    BUCKLER_ID: str = cookies["buckler_id"]
    BUCKLER_R_ID: str = cookies["buckler_r_id"]
    BUCKLER_PRAISE_DATE: str = cookies["buckler_praise_date"]

    if len(sys.argv) == 1:
        print("Mising arguments: -daily | -hist | -init [-debug -all]")

    DEBUG_FLAG = False

    if "-debug" in sys.argv[1:]:
        DEBUG_FLAG = True

    cfn_scraper = CFNStatsScraper(
        datetime.now(),
        DEBUG_FLAG,
        cfn_secrets.NOTIFY_CHANNEL,
        cfn_secrets.URL_TOKEN,
        BUCKLER_ID,
        BUCKLER_R_ID,
        BUCKLER_PRAISE_DATE,
        cfn_secrets.DEFAULT_PLAYER_ID,
    )

    cfn_parser = CFNStatsParser(DEBUG_FLAG, cfn_secrets.NOTIFY_CHANNEL)

    if "-init" in sys.argv[1:]:
        init_db()
        sys.exit("Databases initialized.")

    if "-daily" in sys.argv[1:]:
        # Start Scraping
        start_last_update(date=cfn_scraper.date)
        # club
        cfn_scraper.sync_club_info(cfn_secrets.DEFAULT_CLUB_ID)
        # players
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
        log_last_update(date=cfn_scraper.date, download_complete=True)

        # Start Parsing
        cfn_parser.update_stats_for_date(datetime.now())
        cfn_parser.update_member_list(cfn_secrets.DEFAULT_CLUB_ID)
        cfn_parser.send_push_alert(
            f"[OK] FSN Update {datetime.today().date().strftime('%b %d %Y')}"
        )
        log_last_update(date=cfn_scraper.date, parsing_complete=True)
        sys.exit("Daily run completed.")
    elif "-hist" in sys.argv[1:]:
        historical_dates = cfn_parser.historical_dates
        for hist_date in historical_dates:
            start_last_update(hist_date)
            cfn_parser.update_stats_for_date(hist_date)
            log_last_update(
                date=hist_date, parsing_complete=True, download_complete=True
            )
        sys.exit("Historical backup completed.")
