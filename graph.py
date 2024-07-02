"""Testing graphs"""

import sqlite3

import jinja2
import pandas as pd
import plotly.express as px


def output_graph():

    # data_canada = px.data.gapminder().query("country == 'Canada'")

    output_html_path = r"output.html"
    input_template_path = r"template.html"

    conn = sqlite3.connect("cfn-stats.db")

    df = pd.read_sql_query("SELECT * FROM ranking WHERE player_id='3425126856'", conn)

    fig = px.line(df, x="date", y="lp", title="Scrub: League Points", color="char_id")

    plotly_jinja_data = {"fig": fig.to_html(full_html=False)}
    # consider also defining the include_plotlyjs parameter to point to an external Plotly.js as described above

    with open(output_html_path, "w", encoding="utf-8") as output_file:
        with open(input_template_path, encoding="utf-8") as template_file:
            j2_template = jinja2.Template(template_file.read())
            output_file.write(j2_template.render(plotly_jinja_data))


if __name__ == "__main__":
    output_graph()
