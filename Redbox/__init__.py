import os
from datetime import timedelta
from flask import Flask, render_template

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        # a default secret that should be overridden by instance config
        SECRET_KEY="U9xxQBQZom1MfKw2InBgkQ",
        # store the database in the instance folder
        DATABASE="redbox.db",
        IMAGE_UPLOADS = "./static/assets/img/uploads/",
        PERMANENT_SESSION_LIFETIME = timedelta(days=30),
    )

    if not os.path.isfile("redbox.db"):
        raise IOError("File : redbox.db not found")

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template("404.html"), 404

    from Redbox import views, auth, presse, actualites

    app.register_blueprint(views.bp)
    app.register_blueprint(auth.bp)
    app.register_blueprint(presse.bp)
    app.register_blueprint(actualites.bp)

    return app