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
################################################


from flask import Flask, render_template, request, session
import backend
import data
import re


def get_symbol(pattern):  # backend.py kärbitud funktsioon
    dictionary = data.database
    while True:
        bond_names = []
        for key in dictionary:
            result = re.search(pattern, key, re.IGNORECASE)
            if result:
                bond_names += [key]
        return bond_names


app = Flask(__name__)
app.secret_key = "RobertiJaHendrikuProjekt"


@app.route("/", methods=["GET", "POST"])
def index():
# Kasutame selleks, et salvestada muutujat, kui nuppu vajutatakse teist korda.
    symbol_match = session.get("symbol_match", None) 
    time = session.get("time", None)

    if request.method == "POST": 
        if "symbol" in request.form:  # Esimene HTML form
            symbol = request.form.get("symbol")  # HTML input välja sisend
            period = request.form.get("period")  # HTML select välja sisend
            symbol_match = get_symbol(symbol)
            time = backend.get_dates(period)  # Kasutame backend.py funktsiooni

            session["symbol_match"] = symbol_match # Salvestame muutuja
            session["time"] = time
            return render_template("index.html", symbol_match=symbol_match)

        elif "number" in request.form:  # Teine HTML form
            number = int(request.form.get("number"))
            if number == 0:
                number = 1
            bond = symbol_match[number - 1]

            dictionary = data.database
            if bond in dictionary:
                bond_symbol = dictionary[bond]  # Saame võlakirja tähise

# Kasutame backend.py funktsiooni main, mis väljastab võlakirja hinnad
            prices = backend.main(bond_symbol, time)

            bond_labels = []
            bond_data = []
            tehingute_arv = []
            for el in prices:
                bond_labels.append(el[2])
                bond_data.append(el[0])
                tehingute_arv.append(el[1])

            return render_template("index.html", prices=prices, bond_labels=bond_labels, bond_data=bond_data, tehingute_arv=tehingute_arv)
    else:
        return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)
