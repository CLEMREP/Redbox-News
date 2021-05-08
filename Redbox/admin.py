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
from werkzeug.security import generate_password_hash

bp = Blueprint("admin", __name__, url_prefix="/admin")

@bp.route('/')
def admin():
    try:
        connexion = sqlite3.connect(current_app.config["DATABASE"])
        cursor = connexion.cursor()

    except:
        flash("Une erreur est survenue, ressayer plus tard.")

    else:
        if "email" in session:
            email = session["email"]

            cursor.execute(f"SELECT admin FROM journaliste WHERE email = ( {repr(email)} );")
            admin = cursor.fetchone()

            cursor.execute(f"SELECT id, prenom, nom, email, admin, telephone, ville FROM journaliste")
            journalistes = cursor.fetchall()

            if admin[0] == 1:
                return render_template("admin/index.html", journalistes=journalistes)

            else:
                return redirect(url_for("presse.home"))

        else:
            return redirect(url_for("presse.home"))

@bp.route("/modification-journaliste/<id>", methods=["POST", "GET"])
def modification_journaliste(id):
    try:
        connexion = sqlite3.connect(current_app.config["DATABASE"])
        cursor = connexion.cursor()
        cursor.execute(f"SELECT prenom, nom, email, password, admin, telephone, ville FROM journaliste WHERE id = { repr(id) };")
        infos_journaliste = cursor.fetchall()

    except:
        flash("Problème de connexion, ressayer plus tard.")

    else:
        if "email" in session:
            email = session["email"]

            cursor.execute(f"SELECT admin FROM journaliste WHERE email = ( {repr(email)} );")   
            admin = cursor.fetchone()

            if admin[0] == 1:
                if request.method == 'POST':
                    new_nom = request.form["nom"]
                    new_prenom = request.form["prenom"]
                    new_tel = request.form["telephone"]
                    new_ville = request.form["ville"]
                    new_email = request.form["email"]
                    new_password = request.form["password"]
                    new_admin = request.form["admin"]

                    try:
                        cursor.execute(f"UPDATE journaliste SET prenom = { repr(new_prenom) }, nom = { repr(new_nom) }, email = { repr(new_email) }, password = { repr(generate_password_hash(new_password)) }, admin = { repr(new_admin) }, telephone = { repr(new_tel) }, ville = { repr(new_ville) } WHERE id = { repr(id) };")
                        connexion.commit()

                    except:
                        flash("Problème de connexion, ressayer plus tard.")

                    else:
                        connexion.close()
                        flash("Le compte a été modifié avec succès.")
                        return redirect(url_for('admin.admin'))

            else:
                return redirect(url_for('presse.home'))
        else:
            return redirect(url_for('presse.home'))
        
    return render_template("admin/modification-journaliste.html", infos_journaliste = infos_journaliste)


@bp.route("/supprimer/<id>", methods=["POST", "GET"])
def supprimer(id):
    if request.method == "POST":
        try:
            connexion = sqlite3.connect(current_app.config["DATABASE"])
            cursor = connexion.cursor()
            
            cursor.execute(f"DELETE FROM journaliste WHERE id = { repr(id) }")
            connexion.commit()

        except:
            flash("Erreur lors de la suppresion de l'article.")

        else:
            connexion.close()
            flash(f"Compte { repr(id) } supprimé avec succès !")
            return redirect(url_for('admin.admin'))

    return redirect(url_for('admin.admin'))

@bp.route("/articles")
def articles():
    try:
        connexion = sqlite3.connect(current_app.config["DATABASE"])
        cursor = connexion.cursor()

    except:
        flash("Une erreur est survenue, ressayer plus tard.")

    else:
        if "email" in session:
            email = session["email"]

            cursor.execute(f"SELECT admin FROM journaliste WHERE email = ( {repr(email)} );")
            admin = cursor.fetchone()

            cursor.execute(f"SELECT id, titre, texte, date_publication FROM article")
            articles = cursor.fetchall()

            if admin[0] == 1:
                return render_template("admin/articles.html", articles = articles)

            else:
                return redirect(url_for("presse.home"))

        else:
            return redirect(url_for("presse.home"))


@bp.route("/modification-article/<id>", methods=["POST", "GET"])
def modification_article(id):
    try:
        connexion = sqlite3.connect(current_app.config["DATABASE"])
        cursor = connexion.cursor()
        cursor.execute(f"SELECT id, titre, texte, lien FROM article WHERE id = { repr(id) };")
        infos_articles = cursor.fetchall()

    except:
        flash("Problème de connexion, ressayer plus tard.")

    else:
        if "email" in session:
            email = session["email"]

            cursor.execute(f"SELECT admin FROM journaliste WHERE email = ( {repr(email)} );")   
            admin = cursor.fetchone()

            if admin[0] == 1:

                if request.method == "POST":
                    new_titre = request.form["new_titre"]
                    new_texte = request.form["new_texte"]
                    new_image = request.files["new_file"]

                    new_date = str(datetime.now().strftime("%d/%m/%Y à %Hh%M"))

                    if new_titre == "" or new_texte == "":
                            flash("Merci de remplir tous les champs.")
                            return redirect(url_for('admin.modification_article', id=id))

                    else:
                        try:
                            mon_image = new_image.filename.replace(" ", "_").lower()
                            new_image.save(os.path.join(current_app.config["IMAGE_UPLOADS"], mon_image))
                            lien_image = f"./static/assets/img/uploads/{ repr(mon_image)}".replace("'", "")

                        except:
                            flash("Merci de mettre une image à l'article.")
                            return redirect(url_for('admin.modification_article', id=id))

                    try:
                        cursor.execute(f"UPDATE article SET titre = { repr(new_titre) }, texte = { repr(new_texte) }, lien = { repr(lien_image) }, date_publication = { repr(new_date) } WHERE id = { repr(id) };")
                        connexion.commit()

                    except:
                        flash("Problème de connexion, ressayer plus tard.")

                    else:
                        connexion.close()
                        flash("L'article a été modifié avec succès.")
                        return redirect(url_for('admin.articles'))

            else:
                return redirect(url_for('presse.home'))

        else:
            return redirect(url_for('presse.home'))

    return render_template("admin/modification-article.html", infos_articles = infos_articles)

@bp.route("/supprimer-article/<id>", methods=["POST", "GET"])
def supprimer_articles(id):
    if request.method == "POST":
        try:
            connexion = sqlite3.connect(current_app.config["DATABASE"])
            cursor = connexion.cursor()
            cursor.execute(f"DELETE FROM article WHERE id = { repr(id) }")
            connexion.commit()

        except:
            flash("Erreur lors de la suppresion de l'article.")

        else:
            connexion.close()
            flash(f"Article { repr(id) } supprimé avec succès !")
            return redirect(url_for('admin.articles'))

    return redirect(url_for('admin.articles'))
