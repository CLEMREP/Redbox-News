import sqlite3, os
from datetime import datetime

from flask import Blueprint
from flask import current_app
from flask import flash
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import session
from flask import url_for

bp = Blueprint("actualites", __name__, url_prefix="/actualites")

@bp.route("/<url>")
def actualites(url):
    try:
        connexion = sqlite3.connect(current_app.config["DATABASE"])
        cursor = connexion.cursor()

        cursor.execute(f"SELECT id_journaliste FROM article WHERE url = { repr(url) }")
        identifiant = cursor.fetchone()

        cursor.execute(f"SELECT nom, prenom FROM journaliste JOIN article ON journaliste.id = article.id_journaliste WHERE journaliste.id = { repr(identifiant[0]) }")
        infoJournaliste = cursor.fetchone()
        journaliste = " ".join(infoJournaliste)

        cursor.execute(f"SELECT * FROM article WHERE url = { repr(url) }")
        informationsArticles = cursor.fetchall()

        connexion.commit()
        connexion.close()

    except:
        flash("Problème de connexixon, ressayer plus tard.")

    return render_template("actualites/index.html", informationsArticles=informationsArticles, journaliste=journaliste)