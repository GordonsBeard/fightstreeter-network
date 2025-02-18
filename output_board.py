from datetime import datetime
from zoneinfo import ZoneInfo

from jinja2 import Environment, FileSystemLoader

from fightstreeter.awards import generate_awards
from fightstreeter.leaderboards import generate_leaderboards

env = Environment(loader=FileSystemLoader("templates"))
template = env.get_template("club_leaderboards.html.j2")


top_10_boards, top_10_grouped = generate_leaderboards()
awards_list = generate_awards()

output_from_parsed_template = template.render(
    top_10_boards=top_10_boards, top_10_grouped=top_10_grouped, awards_list=awards_list
)

# TODO:
# turn this into something that can be run automatically based on date

today_file = datetime.now(tz=ZoneInfo("America/Los_Angeles")).strftime(
    "%Y-%m-%d_board.html.j2"
)
today_file = "output_html/" + today_file

# to save the results
with open(today_file, "w", encoding="utf-8") as fh:
    fh.write(output_from_parsed_template)
