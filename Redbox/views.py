import sqlite3

from flask import Blueprint
from flask import current_app
from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import session
from flask import url_for

bp = Blueprint("views", __name__)

@bp.route("/")
def home():
    try:
        connexion = sqlite3.connect(current_app.config["DATABASE"])
        cursor = connexion.cursor()

        articles = cursor.execute("SELECT * FROM article ORDER BY date_publication DESC").fetchall()
        #articles = cursor.fetchall()

        #connexion.commit()
        connexion.close()

    except:
        flash("Problème de connexion, ressayer plus tard.")

    return render_template("index.html", articles=articles)

@bp.route("/a-propos-de-nous")
def a_propos_de_nous():
    return render_template("a-propos-de-nous.html")

@bp.route("/logout")
def logout():
    try:
        session.pop("email", None)
        flash("Vous avez bien été déconnecté.")
        return redirect(url_for("authentification.acces_presse"))

    except:
        flash("Erreur lors de la deconnexion.")