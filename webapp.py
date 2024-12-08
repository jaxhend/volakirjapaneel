################################################
# Programmeerimine I
# 2024/2025 sügissemester
#
# Projekt
# Teema: Balti turu võlakirjapaneel
# Kirjeldus:
# Luua programm, mis näitab Balti turu võlakirju puudutavat
# infot mugavamalt kui olemasoleval LHV leheküljel.
#
#
# Autorid: Hendrik Jaks, Robert Ilves
#
# Mõningane eeskuju:
# LHV internetipanga võlakirjade ost/müük sektsioon
#
# Lisakommentaar (nt käivitusjuhend):
#
# pip install beautifulsoup4
# pip install requests
# pip install virtualenv
# pip install flask
# pip install Flask-Session
# minna CMD's programmi kausta ning python webapp.py
#
# Kasutatud materjalid:
# https://medium.com/@moraneus/python-flask-a-comprehensive-guide-from-basic-to-advanced-fbc6ec9aa5f7
# https://courses.cs.ut.ee/2024/programmeerimine/fall/Main/SilmaringVeebisisuParsimine
# https://courses.cs.ut.ee/2024/programmeerimine/fall/Main/SilmaringVeebirakendus
# https://courses.cs.ut.ee/2024/programmeerimine/fall/Main/SilmaringRegex
# https://flask.palletsprojects.com/en/stable/quickstart/
# https://jinja.palletsprojects.com/en/stable/templates/
# https://www.geeksforgeeks.org/how-to-add-graphs-to-flask-apps/
# https://www.geeksforgeeks.org/autocomplete-input-suggestion-using-python-and-flask/
################################################


from flask import Flask, render_template, request, session
import backend
import data
import re


def get_symbol(pattern):  # backend.py kärbitud funktsioon
    dictionary = data.database
    bond_names = []
    for key in dictionary:
        result = re.search(pattern, key, re.IGNORECASE)
        if result:
            bond_names.append(key)
    return bond_names


app = Flask(__name__)
app.secret_key = "RobertiJaHendrikuProjekt"


@app.route("/", methods=["GET", "POST"])
def index():
# Kasutame selleks, et salvestada muutujat, kui nuppu vajutatakse teist korda.
    all_symbols = list(data.database.keys())
    symbol_match = [] 
    prices = []

    if request.method == "POST": 
        if "symbol" in request.form:
            symbol = request.form.get("symbol")  # HTML input välja sisend
            period = request.form.get("period")  # HTML select välja sisend

            symbol_match = get_symbol(symbol)

            if symbol_match:
                time = backend.get_dates(period)
                bond_symbol = data.database[symbol_match[0]]  # Esimese vaste tähis

                prices = backend.main(bond_symbol, time)

                # Graafiku andmed paremini organiseeritud
                bond_labels = [el[2] for el in prices]
                bond_data = [el[0] for el in prices]
                tehingute_arv = [el[1] for el in prices]

                # Lehe koos graafiku ja dropdown-boxi andmetega renderdamine
                return render_template(
                    "index.html",
                    all_symbols=all_symbols,
                    symbol_match=symbol_match,
                    prices=prices,
                    bond_labels=bond_labels,
                    bond_data=bond_data,
                    tehingute_arv=tehingute_arv,
                )
            else:
                # Juhul kui võlakirja ei leidu
                return render_template(
                    "index.html",
                    all_symbols=all_symbols,
                    symbol_match=symbol_match,
                    message="Vastavat võlakirja ei leitud.",
                )
    
    return render_template(
        "index.html",
        all_symbols=all_symbols,
        symbol_match=symbol_match
    )

if __name__ == "__main__":
    app.run(debug=True)
