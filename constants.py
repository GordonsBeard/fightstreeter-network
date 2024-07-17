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
    "27": "27",
    "28": "28",
    "29": "29",
    "30": "30",
}

league_ranks: dict[int, str] = {
    0: "Rookie 1",
    200: "Rookie 2",
    400: "Rookie 3",
    600: "Rookie 4",
    800: "Rookie 5",
    1000: "Iron 1",
    1400: "Iron 2",
    1800: "Iron 3",
    2200: "Iron 4",
    2600: "Iron 5",
    3000: "Bronze 1",
    3400: "Bronze 2",
    3800: "Bronze 3",
    4200: "Bronze 4",
    4600: "Bronze 5",
    5000: "Silver 1",
    5800: "Silver 2",
    6600: "Silver 3",
    7400: "Silver 4",
    8200: "Silver 5",
    9000: "Gold 1",
    9800: "Gold 2",
    10600: "Gold 3",
    11400: "Gold 4",
    12200: "Gold 5",
    13000: "Platinum 1",
    14200: "Platinum 2",
    15400: "Platinum 3",
    16600: "Platinum 4",
    17800: "Platinum 5",
    19000: "Diamond 1",
    20200: "Diamond 2",
    21400: "Diamond 3",
    22600: "Diamond 4",
    23800: "Diamond 5",
    25000: "Master",
}


def get_league_class(lp) -> str:
    """Takes the players LP and returns the appropriate class name for HTML colors."""
    class_name: str = ""

    if 0 <= lp < 200:
        class_name = "r1"
    elif 200 <= lp < 400:
        class_name = "r-2"
    elif 400 <= lp < 600:
        class_name = "r-3"
    elif 600 <= lp < 800:
        class_name = "r-4"
    elif 800 <= lp < 1000:
        class_name = "r-5"

    elif 1000 <= lp < 1400:
        class_name = "i-1"
    elif 1400 <= lp < 1800:
        class_name = "i-2"
    elif 1800 <= lp < 2200:
        class_name = "i-3"
    elif 2200 <= lp < 2600:
        class_name = "i-4"
    elif 2600 <= lp < 3000:
        class_name = "i-5"

    elif 3000 <= lp < 3400:
        class_name = "b-1"
    elif 3400 <= lp < 3800:
        class_name = "b-2"
    elif 3800 <= lp < 4200:
        class_name = "b-3"
    elif 4200 <= lp < 4600:
        class_name = "b-4"
    elif 4600 <= lp < 5000:
        class_name = "b-5"

    elif 5000 <= lp < 5800:
        class_name = "s-1"
    elif 5800 <= lp < 6600:
        class_name = "s-2"
    elif 6600 <= lp < 7400:
        class_name = "s-3"
    elif 7400 <= lp < 8200:
        class_name = "s-4"
    elif 8200 <= lp < 9000:
        class_name = "s-5"

    elif 9000 <= lp < 9800:
        class_name = "g-1"
    elif 9800 <= lp < 10600:
        class_name = "g-2"
    elif 10600 <= lp < 11400:
        class_name = "g-3"
    elif 11400 <= lp < 12200:
        class_name = "g-4"
    elif 12200 <= lp < 13000:
        class_name = "g-5"

    elif 13000 <= lp < 14200:
        class_name = "p-1"
    elif 14200 <= lp < 15400:
        class_name = "p-2"
    elif 15400 <= lp < 16600:
        class_name = "p-3"
    elif 16600 <= lp < 17800:
        class_name = "p-4"
    elif 17800 <= lp < 19000:
        class_name = "p-5"

    elif 19000 <= lp < 20200:
        class_name = "d-1"
    elif 20200 <= lp < 21400:
        class_name = "d-2"
    elif 21400 <= lp < 22600:
        class_name = "d-3"
    elif 22600 <= lp < 23800:
        class_name = "d-4"
    elif 23800 <= lp < 25000:
        class_name = "d-5"

    elif lp >= 25000:
        class_name = "m"
    return class_name


def get_mr_class(mr) -> str:
    """Takes the players LP and returns the appropriate class name for HTML colors."""

    class_name = ""

    if 0 <= mr < 1500:
        class_name = "mr-low"
    elif mr == 1500:
        class_name = "mr-15"
    elif 1500 <= mr < 1600:
        class_name = "mr-16"
    elif 1600 <= mr < 1700:
        class_name = "mr-17"
    elif 1700 <= mr < 1800:
        class_name = "mr-18"
    elif 1800 <= mr:
        class_name = "mr-high"

    return class_name


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
    "1994931079",
    "2172475021",
    "2220983103",  # inttena/zain
    "2251667984",  # geight
    "2312128654",
    "2380532183",
    "2531364579",  # Sugar Meowth
    "2703886514",  # crud
    "2881725645",
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
    "3022660117",  # shay
]
