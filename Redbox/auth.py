import sqlite3
from datetime import date

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

from Redbox.verifForm import validateFormConnexion, validateForm


bp = Blueprint("authentification", __name__, url_prefix="/authentification")

@bp.route('/acces-presse', methods=["POST", "GET"])
def acces_presse():            
    try:
        connexion = sqlite3.connect(current_app.config["DATABASE"])
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
                return redirect(url_for('presse.home'))

            if "email" in session:
                return redirect(url_for('presse.home'))


    return render_template("authentification/acces-presse.html")

@bp.route("/demande-presse", methods=["POST", "GET"])
def demande_presse():
    try:
        connexion = sqlite3.connect(current_app.config["DATABASE"])
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

            admin = 0
            creation_date = str(date.today())

            isInvalidForm = validateForm(prenom, nom, telephone, ville, email, password, confirm_password, cursor)

            if isInvalidForm:
                for errors in isInvalidForm.split("\n")[:-1]:
                    flash(errors)

            else:
                try:
                    pswd = generate_password_hash(password)
                    
                    cursor.execute(f"INSERT INTO journaliste (prenom, nom, email, password, admin, telephone, ville, date_creation) VALUES ({ repr(prenom) }, { repr(nom) }, { repr(email) }, { repr(pswd) }, { repr(admin) }, { repr(telephone) }, { repr(ville) }, { repr(creation_date) });")
                    connexion.commit()

                except:
                    flash("Problème de connexion, ressayer plus tard.")

                else:
                    connexion.close()
                    flash("Création du compte avec succès.")
                    return redirect(url_for('authentification.acces_presse'))


    return render_template("authentification/demande-presse.html")

@bp.route("/logout")
def logout():
    try:
        session.pop("email", None)
        flash("Vous avez bien été déconnecté.")
        return redirect(url_for("authentification.acces_presse"))

    except:
        flash("Erreur lors de la deconnexion.")
