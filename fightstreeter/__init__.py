"""fight streeter website, just some street fighter stats tracking"""

# pylint: disable=C
import os

from flask import Flask


def create_app(test_config=None):
    """Create and configure the flask app"""
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(DATABASE=os.path.join(app.instance_path, "cfn-stats.db"))

    if not test_config:
        app.config.from_pyfile("config.py", silent=True)
    else:
        app.config.from_mapping(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.route("/")
    def index():
        return roster.roster()

    from . import db

    db.init_app(app)

    with app.app_context():
        from . import leaderboards

        app.register_blueprint(leaderboards.bp)

        from . import roster

        app.register_blueprint(roster.bp)

        from . import player

        app.register_blueprint(player.bp)
    return app
