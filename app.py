import sqlite3, os

from flask import Flask, render_template, redirect, flash, request, url_for, session
from string import printable
from datetime import *
from verifFormPresse import *

app = Flask(__name__)

app.secret_key = "cR250603*"
app.permanent_session_lifetime = timedelta(days=30)
app.config["IMAGE_UPLOADS"] = "./static/assets/img/uploads/"

DATABASE = "redbox_bdd.db"

@app.route("/")
def home():
    try:
        connexion = sqlite3.connect(DATABASE)
        cursor = connexion.cursor()

        cursor.execute(f"SELECT * FROM article ORDER BY date_publication DESC")
        articles = cursor.fetchall()

        connexion.commit()
        connexion.close()

    except:
        flash("Problème de connexion, ressayer plus tard.")

    return render_template("index.html", articles=articles)

@app.route("/actualites/<titre>")
def actualites(titre):
    try:
        connexion = sqlite3.connect(DATABASE)
        cursor = connexion.cursor()

        cursor.execute(f"SELECT id_journaliste FROM article WHERE titre = { repr(titre) }")
        identifiant = cursor.fetchone()

        cursor.execute(f"SELECT nom, prenom FROM journaliste JOIN article ON journaliste.id = article.id_journaliste WHERE journaliste.id = { repr(identifiant[0]) }")
        infoJournaliste = cursor.fetchone()
        journaliste = " ".join(infoJournaliste)

        cursor.execute(f"SELECT * FROM article WHERE titre = { repr(titre) }")
        informationsArticles = cursor.fetchall()

        connexion.commit()
        connexion.close()

    except:
        flash("Problème de connexixon, ressayer plus tard.")

    return render_template("/actualites/index.html", informationsArticles=informationsArticles, journaliste=journaliste)


@app.route("/a-propos-de-nous")
def a_propos_de_nous():
    return render_template("a-propos-de-nous.html")


@app.route('/acces-presse', methods=('GET', 'POST'))
def acces_presse():            
    try:
        connexion = sqlite3.connect(DATABASE)
        cursor = connexion.cursor()

    except:
        flash("Une erreur est survenue, ressayer plus tard.")

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        session["email"] = email
        
        isInvalidFormConnect = validateFormConnexion(email, password, cursor)

        if isInvalidFormConnect:
            for errors in isInvalidFormConnect.split("\n"):
                flash(errors)

        else:
            try:
                connexion.commit()
            
            except:
                flash("Problème de connexion, ressayer plus tard.")

            else:
                connexion.close()
                return redirect(url_for('presse'))

            if "email" in session:
                return redirect(url_for('presse'))


    return render_template("acces-presse.html")

@app.route("/demande-presse", methods=('GET', 'POST'))
def demande_presse():
    try:
        connexion = sqlite3.connect(DATABASE)
        cursor = connexion.cursor()

    except:
        flash("Une erreur est survenue, ressayer plus tard.")

    else:
        if request.method == 'POST':
            nom = request.form["nom"]
            prenom = request.form["prenom"]
            telephone = request.form["telephone"]
            ville = request.form["ville"]
            email = request.form["email_inscription"]
            password = request.form["password_inscription"]
            confirm_password = request.form["confirm_password"]

            creation_date = str(date.today())

            isInvalidForm = validateForm(prenom, nom, telephone, ville, email, password, confirm_password, cursor)

            if isInvalidForm:
                for errors in isInvalidForm.split("\n")[:-1]:
                    flash(errors)

            else:
                try:
                    cursor.execute(f"INSERT INTO journaliste (prenom, nom, email, password, telephone, ville, date_creation) VALUES ({ repr(prenom) }, { repr(nom) }, { repr(email) }, { repr(password) }, { repr(telephone) }, { repr(ville) }, { repr(creation_date) });")
                    connexion.commit()

                except:
                    flash("Problème de connexion, ressayer plus tard.")

                else:
                    connexion.close()
                    flash("Création du compte avec succès.")
                    return redirect(url_for('acces_presse'))


    return render_template("demande-presse.html")

@app.route("/presse/", methods=["POST", "GET"])
def presse():
    try:
        connexion = sqlite3.connect(DATABASE)
        cursor = connexion.cursor()

    except:
        flash("Problème de connexion, ressayer plus tard.")

    else:
        if "email" in session:
            email = session["email"]

            cursor.execute(f"SELECT COUNT(id) FROM article")
            nbArticle = cursor.fetchone()

            cursor.execute(f"SELECT prenom, nom FROM journaliste WHERE email = ( {repr(email)} );")
            pseudo = cursor.fetchone()

            cursor.execute(f"SELECT id FROM journaliste WHERE email = ({ repr(email) });")
            identifiant = cursor.fetchone()

            cursor.execute(f"SELECT COUNT(id) FROM article WHERE id_journaliste = ({ repr(identifiant[0]) });")
            nbArticlePublie = cursor.fetchone()

            connexion.commit()

            return render_template("/presse/index.html", pseudo=" ".join(pseudo), nbArticle=nbArticle[0], nbArticlePublie=nbArticlePublie[0])

        else:
            return redirect(url_for('acces_presse'))

@app.route("/presse/mes-articles")
def mes_articles():
    if "email" in session:
            email = session["email"]

            try:
                connexion = sqlite3.connect(DATABASE)
                cursor = connexion.cursor()

                cursor.execute(f"SELECT id FROM journaliste WHERE email = ({ repr(email) });")
                identifiant = cursor.fetchone()

                cursor.execute(f"SELECT * FROM article WHERE id_journaliste = ({ repr(identifiant[0]) }) ORDER BY date_publication DESC")
                articles = cursor.fetchall()

                connexion.commit()
                connexion.close()

            except:
                flash("Problème de connexion, ressayer plus tard.")

    else:
        return redirect(url_for('acces_presse'))

    return render_template("/presse/mes-articles.html", articles=articles)

@app.route("/presse/publier-article", methods=["POST", "GET"])
def publier_articles():
    try:
        connexion = sqlite3.connect(DATABASE)
        cursor = connexion.cursor()

    except:
        flash("Une erreur est survenue, ressayer plus tard.")

    else:
        if "email" in session:
            email = session["email"]

            if request.method == 'POST':
                titre = request.form["titre"]
                texte = request.form["texte"]
                image = request.files["file"]

                creation_date = str(datetime.now().strftime("%d/%m/%Y à %Hh%M"))

                if titre == "" or texte == "":
                    flash("Merci de remplir tous les champs.")
                    return redirect(url_for('publier_articles'))

                else:
                    try:
                        mon_image = image.filename.replace(" ", "_").lower()
                        image.save(os.path.join(app.config["IMAGE_UPLOADS"], mon_image))
                        lien_image = f"./static/assets/img/uploads/{ repr(mon_image)}".replace("'", "")

                    except:
                        flash("Merci de mettre une image à l'article.")
                        return redirect(url_for('publier_articles'))

                try:
                    cursor.execute(f"SELECT id FROM journaliste WHERE email = ({ repr(email) });")
                    identifiant = cursor.fetchone()
                    cursor.execute(f"INSERT INTO article (id_journaliste, titre, texte, lien, date_publication) VALUES ({ repr(identifiant[0]) }, { repr(titre) }, { repr(texte) }, { repr(lien_image) }, { repr(creation_date) } );")
                    connexion.commit()

                except:
                    flash("Problème de connexion, ressayer plus tard.")

                else:
                    connexion.close()
                    flash("L'article a été publié avec succès.")

        else:
            return redirect(url_for('acces_presse'))

    return render_template("/presse/publier-article.html")

@app.route("/presse/supprimer/<id>", methods=["POST", "GET"])
def supprimer(id):
    if request.method == "POST":
        try:
            connexion = sqlite3.connect(DATABASE)
            cursor = connexion.cursor()
            cursor.execute(f"DELETE FROM article WHERE id = { repr(id) }")
            connexion.commit()

        except:
            flash("Erreur lors de la suppresion de l'article.")

        else:
            connexion.close()
            flash(f"Article { repr(id) } supprimé avec succès !")
            return redirect(url_for('mes_articles'))

    return redirect(url_for('mes_articles'))

@app.route("/presse/modifier-article/<id>", methods=["POST", "GET"])
def modifier_article(id):
    try:
        connexion = sqlite3.connect(DATABASE)
        cursor = connexion.cursor()
        cursor.execute(f"SELECT id, titre, texte, lien FROM article WHERE id = { repr(id) };")
        infos_articles = cursor.fetchall()

    except:
        flash("Problème de connexion, ressayer plus tard.")

    else:
        if "email" in session:
            email = session["email"]

            if request.method == "POST":
                new_titre = request.form["new_titre"]
                new_texte = request.form["new_texte"]
                new_image = request.files["new_file"]

                new_date = str(datetime.now().strftime("%d/%m/%Y à %Hh%M"))

                if new_titre == "" or new_texte == "":
                        flash("Merci de remplir tous les champs.")
                        return redirect(url_for('modifier_article', id=id))
                    
                else:
                    try:
                        mon_image = new_image.filename.replace(" ", "_").lower()
                        new_image.save(os.path.join(app.config["IMAGE_UPLOADS"], mon_image))
                        lien_image = f"./static/assets/img/uploads/{ repr(mon_image)}".replace("'", "")

                    except:
                        flash("Merci de mettre une image à l'article.")
                        return redirect(url_for('modifier_article', id=id))

                try:
                    cursor.execute(f"UPDATE article SET titre = { repr(new_titre) }, texte = { repr(new_texte) }, lien = { repr(lien_image) }, date_publication = { repr(new_date) } WHERE id = { repr(id) };")
                    connexion.commit()

                except:
                    flash("Problème de connexion, ressayer plus tard.")

                else:
                    connexion.close()
                    flash("L'article a été modifié avec succès.")
                    return redirect(url_for('mes_articles'))

        else:
            return redirect(url_for('acces_presse'))

    return render_template("/presse/modifier-article.html", infos_articles = infos_articles)


@app.route("/presse/mon-compte", methods=["POST", "GET"])
def mon_compte():
    if "email" in session:
            email = session["email"]

            try:
                connexion = sqlite3.connect(DATABASE)
                cursor = connexion.cursor()
                cursor.execute(f"SELECT * FROM journaliste WHERE email = ({ repr(email) });")
                informations = cursor.fetchone()
                connexion.commit()

            except:
                flash("Problème de connexion, ressayer plus tard.")

            else:
                connexion.close()

                if request.method == 'POST':
                    new_email = request.form["new_email"]
                    new_password = request.form["new_password"]

                    try:
                        connexion = sqlite3.connect(DATABASE)
                        cursor = connexion.cursor()
                        cursor.execute(f"UPDATE journaliste SET email = { repr(new_email) }, password = { repr(new_password) }")
                        connexion.commit()

                    except:
                        flash("Problème de connexion, ressayer plus tard.")

                    else:
                        connexion.close()
                        flash("Le compte a bien été modifié.")
                        return redirect(url_for('mon_compte'))

    else:
        return redirect(url_for('acces_presse'))

    return render_template("/presse/mon-compte.html", informations=informations)

@app.route("/logout")
def logout():
    try:
        session.pop("email", None)
        flash("Vous avez bien été déconnecté.")
        return redirect(url_for("acces_presse"))

    except:
        flash("Erreur lors de la deconnexion.")

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=80)
