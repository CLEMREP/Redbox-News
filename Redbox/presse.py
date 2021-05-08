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

from werkzeug.security import generate_password_hash, check_password_hash

bp = Blueprint("presse", __name__, url_prefix="/presse")

@bp.route("/", methods=["POST", "GET"])
def home():
    try:
        connexion = sqlite3.connect(current_app.config["DATABASE"])
        cursor = connexion.cursor()

    except:
        flash("Problème de connexion, ressayer plus tard.")

    else:
        if "email" in session:
            email = session["email"]

            cursor.execute(f"SELECT admin FROM journaliste WHERE email = ( {repr(email)} );")   
            admin = cursor.fetchone()

            cursor.execute(f"SELECT COUNT(id) FROM article")
            nbArticle = cursor.fetchone()

            cursor.execute(f"SELECT prenom, nom FROM journaliste WHERE email = ( {repr(email)} );")
            pseudo = cursor.fetchone()

            cursor.execute(f"SELECT id FROM journaliste WHERE email = ({ repr(email) });")
            identifiant = cursor.fetchone()

            cursor.execute(f"SELECT COUNT(id) FROM article WHERE id_journaliste = ({ repr(identifiant[0]) });")
            nbArticlePublie = cursor.fetchone()

            connexion.commit()

            return render_template("presse/index.html", pseudo = " ".join(pseudo), nbArticle = nbArticle[0], nbArticlePublie = nbArticlePublie[0], admin = admin[0])

        else:
            return redirect(url_for('authentification.acces_presse'))

@bp.route("/mes-articles")
def mes_articles():
    if "email" in session:
            email = session["email"]

            try:
                connexion = sqlite3.connect(current_app.config["DATABASE"])
                cursor = connexion.cursor()

                cursor.execute(f"SELECT admin FROM journaliste WHERE email = ( {repr(email)} );")   
                admin = cursor.fetchone()

                cursor.execute(f"SELECT id FROM journaliste WHERE email = ({ repr(email) });")
                identifiant = cursor.fetchone()

                cursor.execute(f"SELECT * FROM article WHERE id_journaliste = ({ repr(identifiant[0]) }) ORDER BY date_publication DESC")
                articles = cursor.fetchall()

                connexion.commit()
                connexion.close()

            except:
                flash("Problème de connexion, ressayer plus tard.")

    else:
        return redirect(url_for('authentification.acces_presse'))

    return render_template("presse/mes-articles.html", articles = articles, admin = admin[0])

@bp.route("/publier-article", methods=["POST", "GET"])
def publier_articles():
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

            if request.method == 'POST':
                titre = request.form["titre"]
                texte = request.form["texte"]
                image = request.files["file"]

                creation_date = str(datetime.now().strftime("%d/%m/%Y à %Hh%M"))
                url = titre.replace(" ", "_").lower()

                if titre == "" or texte == "":
                    flash("Merci de remplir tous les champs.")
                    return redirect(url_for('presse.publier_articles'))

                else:
                    try:
                        mon_image = image.filename.replace(" ", "_").lower()
                        image.save(os.path.join(current_app.config["IMAGE_UPLOADS"], mon_image))
                        lien_image = f"./static/assets/img/uploads/{ repr(mon_image)}".replace("'", "")

                    except:
                        flash("Merci de mettre une image à l'article.")
                        return redirect(url_for('presse.publier_articles'))

                try:
                    cursor.execute(f"SELECT id FROM journaliste WHERE email = ({ repr(email) });")
                    identifiant = cursor.fetchone()

                    cursor.execute(f"INSERT INTO article (id_journaliste, titre, texte, lien, url, date_publication) VALUES ({ repr(identifiant[0]) }, { repr(titre) }, { repr(texte) }, { repr(lien_image) }, { repr(url) }, { repr(creation_date) } );")
                    
                    connexion.commit()

                except:
                    flash("Problème de connexion, ressayer plus tard.")

                else:
                    connexion.close()
                    flash("L'article a été publié avec succès.")

        else:
            return redirect(url_for('authentification.acces_presse'))

    return render_template("presse/publier-article.html", admin = admin[0])

@bp.route("/supprimer/<id>", methods=["POST", "GET"])
def supprimer(id):
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
            return redirect(url_for('presse.mes_articles'))

    return redirect(url_for('presse.mes_articles'))

@bp.route("/modifier-article/<id>", methods=["POST", "GET"])
def modifier_article(id):
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

            if request.method == "POST":
                new_titre = request.form["new_titre"]
                new_texte = request.form["new_texte"]
                new_image = request.files["new_file"]

                new_date = str(datetime.now().strftime("%d/%m/%Y à %Hh%M"))

                if new_titre == "" or new_texte == "":
                        flash("Merci de remplir tous les champs.")
                        return redirect(url_for('presse.modifier_article', id=id))
                    
                else:
                    try:
                        mon_image = new_image.filename.replace(" ", "_").lower()
                        new_image.save(os.path.join(current_app.config["IMAGE_UPLOADS"], mon_image))
                        lien_image = f"./static/assets/img/uploads/{ repr(mon_image)}".replace("'", "")

                    except:
                        flash("Merci de mettre une image à l'article.")
                        return redirect(url_for('presse.modifier_article', id=id))

                try:
                    cursor.execute(f"UPDATE article SET titre = { repr(new_titre) }, texte = { repr(new_texte) }, lien = { repr(lien_image) }, date_publication = { repr(new_date) } WHERE id = { repr(id) };")
                    connexion.commit()

                except:
                    flash("Problème de connexion, ressayer plus tard.")

                else:
                    connexion.close()
                    flash("L'article a été modifié avec succès.")
                    return redirect(url_for('presse.mes_articles'))

        else:
            return redirect(url_for('authentification.acces_presse'))

    return render_template("presse/modifier-article.html", infos_articles = infos_articles, admin = admin[0])

@bp.route("/mon-compte", methods=["POST", "GET"])
def mon_compte():
    if "email" in session:
            email = session["email"]

            try:
                connexion = sqlite3.connect(current_app.config["DATABASE"])
                cursor = connexion.cursor()

                cursor.execute(f"SELECT * FROM journaliste WHERE email = ({ repr(email) });")
                informations = cursor.fetchone()

                cursor.execute(f"SELECT admin FROM journaliste WHERE email = ( {repr(email)} );")   
                admin = cursor.fetchone()

                connexion.commit()

            except:
                flash("Problème de connexion, ressayer plus tard.")

            else:
                connexion.close()

                if request.method == 'POST':
                    new_email = request.form["new_email"]
                    new_password = request.form["new_password"]

                    try:
                        connexion = sqlite3.connect(current_app.config["DATABASE"])
                        cursor = connexion.cursor()

                        cursor.execute(f"SELECT id FROM journaliste WHERE email = ({ repr(email) });")
                        identifiant = cursor.fetchone()
                        
                        cursor.execute(f"UPDATE journaliste SET email = { repr(new_email) }, password = { repr(generate_password_hash(new_password)) } WHERE id = ({ repr(identifiant[0]) })")
                        connexion.commit()

                    except:
                        flash("Problème de connexion, ressayer plus tard.")

                    else:
                        connexion.close()
                        flash("Le compte a bien été modifié.")
                        return redirect(url_for('authentification.logout'))

    else:
        return redirect(url_for('authentification.acces_presse'))

    return render_template("presse/mon-compte.html", informations = informations, admin = admin[0])

@bp.route("/logout")
def logout():
    try:
        session.pop("email", None)
        flash("Vous avez bien été déconnecté.")
        return redirect(url_for("authentification.acces_presse"))

    except:
        flash("Erreur lors de la deconnexion.")