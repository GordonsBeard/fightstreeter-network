"""Gets the value of the login credentials from a provided cookies.txt file."""

import re


def parse_cookie_file(cookies_file: str):
    """Parse a cookies.txt file and return a dictionary of key value pairs compatible with requests."""

    cookie_dict: dict[str, str] = {}
    with open(cookies_file, "r", encoding="utf-8") as fp:
        for line in fp:
            if not re.match(r"^\#", line) and line != "\n":
                line_fields = line.strip().split("\t")
                cookie_dict[line_fields[5]] = line_fields[6]
    return cookie_dict


cookies = parse_cookie_file("cookies.txt")

BUCKLER_ID: str = cookies["buckler_id"]
BUCKLER_R_ID: str = cookies["buckler_r_id"]
BUCKLER_PRAISE_DATE: str = cookies["buckler_praise_date"]
