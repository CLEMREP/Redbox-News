import re
from werkzeug.security import generate_password_hash, check_password_hash

def validateFormConnexion(email, password, cursor):
    error = ""

    if any(not elt for elt in (email, password)):
        error += "Merci de remplir tous les champs."

    if not error:
        cursor.execute(f"SELECT password FROM journaliste WHERE email = ({ repr(email) })")
        pswd = str(cursor.fetchone()).replace("',)", "").replace("('", "")
        if check_password_hash(pswd, password) is not True:
            error += "Email / Mot de passe incorrect."

    if not error:
        cursor.execute(f"SELECT email FROM journaliste WHERE email = ({ repr(email) })")
        elt = str(cursor.fetchone()).replace("',)", "").replace("('", "")
        if elt != email:
            error += "Email / Mot de passe incorrect."

    return error

def validateForm(prenom, nom, telephone, ville, email, password, confirm_password, cursor):
    error = ""
    regex_email = "^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$"
    regex_password = "^.*(?=.{8,})(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[@#$%^&+=]).*$"

    if any(not e for e in (prenom, nom, telephone, ville, email, password, confirm_password)):
        error += "Veuillez remplir tous les champs.\n"
        
    else:
        if not 3 < len(prenom) < 16:
            error += "Le prénom doit faire entre 3 et 16 caractères.\n"

        if not 3 < len(nom) < 16:
            error += "Le nom doit faire entre 3 et 16 caractères.\n"

        if not re.match(regex_email, email):
            error += "L'adresse mail n'est pas valide.\n"

        if not 8 < len(password) < 64:
            error += "Le mot de passe doit faire entre 6 et 16 caractères.\n"

        if password != confirm_password:
            error += "Les mots de passe ne sont pas identiques.\n"

        if not re.match(regex_password, password):
            error += "Merci de renforcer votre mot de passe. Il doit contenir une majuscule, une minuscule, un numéro et un caractère spécial.\n"

        if not error:
            cursor.execute(f"SELECT email FROM journaliste WHERE email = ({ repr(email) });")
            if cursor.fetchone() is not None:
                error += "L'adresse mail est déjà utilisée.\n"
            
    return error
