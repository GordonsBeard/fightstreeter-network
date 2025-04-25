"""fight streeter website, just some street fighter stats tracking"""

# pylint: disable=C
import os

from apiflask import APIFlask
from flask_cors import CORS


def create_app(test_config=None):
    """Create and configure the flask app"""
    app = APIFlask(__name__, instance_relative_config=True)
    app.config.from_mapping(DATABASE=os.path.join(app.instance_path, "cfn-stats.db"))
    CORS(app)

    if not test_config:
        app.config.from_pyfile("config.py", silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from fightstreetapi import db

    db.init_app(app)

    with app.app_context():
        from . import leaderboards

        app.register_blueprint(leaderboards.bp)

        from . import roster

        app.register_blueprint(roster.bp)

        from . import player

        app.register_blueprint(player.bp)

        from . import punchcard

        app.register_blueprint(punchcard.bp)
    return app
