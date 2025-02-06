"""Things I want across the entire project. Please don't tell people how I code."""

charid_map: dict[str, str] = {
    "1": "Ryu",
    "2": "Luke",
    "3": "Kimberly",
    "4": "Chun-Li",
    "5": "Manon",
    "6": "Zangief",
    "7": "JP",
    "8": "Dhalsim",
    "9": "Cammy",
    "10": "Ken",
    "11": "Dee Jay",
    "12": "Lily",
    "13": "A.K.I.",
    "14": "Rashid",
    "15": "Blanka",
    "16": "Juri",
    "17": "Marisa",
    "18": "Guile",
    "19": "Ed",
    "20": "E. Honda",
    "21": "Jamie",
    "22": "Akuma",
    "23": "23",
    "24": "24",
    "25": "25",
    "26": "M. Bison",
    "27": "Terry",
    "28": "Mai",
    "29": "29",
    "30": "30",
}

league_ranks: dict[int, dict[str, str]] = {
    25000: {"name": "Master", "class": "m"},
    23800: {"name": "Diamond 5", "class": "d-5"},
    22600: {"name": "Diamond 4", "class": "d-4"},
    21400: {"name": "Diamond 3", "class": "d-3"},
    20200: {"name": "Diamond 2", "class": "d-2"},
    19000: {"name": "Diamond 1", "class": "d-1"},
    17800: {"name": "Platinum 5", "class": "p-5"},
    16600: {"name": "Platinum 4", "class": "p-4"},
    15400: {"name": "Platinum 3", "class": "p-3"},
    14200: {"name": "Platinum 2", "class": "p-2"},
    13000: {"name": "Platinum 1", "class": "p-1"},
    12200: {"name": "Gold 5", "class": "g-5"},
    11400: {"name": "Gold 4", "class": "g-4"},
    10600: {"name": "Gold 3", "class": "g-3"},
    9800: {"name": "Gold 2", "class": "g-2"},
    9000: {"name": "Gold 1", "class": "g-1"},
    8200: {"name": "Silver 5", "class": "s-5"},
    7400: {"name": "Silver 4", "class": "s-4"},
    6600: {"name": "Silver 3", "class": "s-3"},
    5800: {"name": "Silver 2", "class": "s-2"},
    5000: {"name": "Silver 1", "class": "s-1"},
    4600: {"name": "Bronze 5", "class": "b-5"},
    4200: {"name": "Bronze 4", "class": "b-4"},
    3800: {"name": "Bronze 3", "class": "b-3"},
    3400: {"name": "Bronze 2", "class": "b-2"},
    3000: {"name": "Bronze 1", "class": "b-1"},
    2600: {"name": "Iron 5", "class": "i-5"},
    2200: {"name": "Iron 4", "class": "i-4"},
    1800: {"name": "Iron 3", "class": "i-3"},
    1400: {"name": "Iron 2", "class": "i-2"},
    1000: {"name": "Iron 1", "class": "i-1"},
    800: {"name": "Rookie 5", "class": "r-5"},
    600: {"name": "Rookie 4", "class": "r-4"},
    400: {"name": "Rookie 3", "class": "r-3"},
    200: {"name": "Rookie 2", "class": "r-2"},
    0: {"name": "Rookie 1", "class": "r-1"},
    -1: {"name": "New Challenger", "class": "nc"},
}

mr_league_ranks: dict[int, dict[str, str]] = {
    1800: {"name": "Ultimate Master", "class": "mr-ult"},
    1700: {"name": "Grand Master", "class": "mr-grand"},
    1600: {"name": "High Master", "class": "mr-high"},
    0: {"name": "Master", "class": "mr-def"},
    -1: {"name": "New Master", "class": "nc"},
}


def fetch_league_name(player_lp: int) -> dict[str, str]:
    """Returns the league dictionary with league name and css class."""

    for minrank, league in league_ranks.items():
        if player_lp >= minrank:
            return league

    return league_ranks[-1]


def fetch_mr_league_name(player_mr: int) -> dict[str, str]:
    """Returns the league name for Master rank."""

    for minrank, league in mr_league_ranks.items():
        if player_mr >= minrank:
            return league

    return mr_league_ranks[-1]

    # class_name = ""

    # high = 1400  # 1600
    # grand = 1505  # 1700
    # ult = 1540  # 1800

    # if player_mr < high:
    #     class_name = "mr-def"
    # elif high <= player_mr < grand:
    #     class_name = "mr-high"
    # elif grand <= player_mr < ult:
    #     class_name = "mr-grand"
    # elif ult <= player_mr:
    #     class_name = "mr-ult"

    # return class_name


def get_kudos_class(kudos) -> str:
    """Takes the players Kudos and returns the appropriate class name for HTML colors."""

    class_name = ""
    kudos /= 2

    if 0 <= kudos < 1540:
        class_name = "kud-1"
    elif 1540 <= kudos < 11120:
        class_name = "kud-2"
    elif 11120 <= kudos < 39940:
        class_name = "kud-3"
    elif 39940 <= kudos < 102540:
        class_name = "kud-4"
    elif 102540 < kudos:
        class_name = "kud-5"

    return class_name


FUNNY_ANIMALS: list[str] = [
    "1005019466",
    "1005115021",
    "1074687961",
    "1462060153",
    "1774348616",
    "1818343673",
    "1980173119",  # izzy
    "1994931079",
    "2172475021",  # owlyoop
    "2220983103",  # inttena/zain
    "2251667984",  # geight
    "2312128654",
    "2380532183",
    "2531364579",  # Sugar Meowth
    "2703886514",  # crud
    "2881725645",
    "3022660117",  # shay
    "3215587216",
    "3240817600",  # Array
    "3425126856",  # scrub
    "3444486243",
    "3452142911",
    "3469051697",
    "3585459087",
    "3712336197",
    "3781805743",  # auxy
    "4010969238",
    "4249556471",
]
