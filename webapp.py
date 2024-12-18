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
# https://www.geeksforgeeks.org/autocomplete-input-suggestion-using-python-and-flask/
################################################

# Mina lisan juurde:
# Sellelt leheküljelt infot https://nasdaqbaltic.com/statistics/et/instrument/EE3300002047/security
# YTM kalkulaator
# (võimalus valida kuupäevi)


# Sina (Robert):
# Pane see fail käima ja sa näed et nüüd on vastavalt kuupäev, hind1, hind2 ja kogus
# Hind1 on ilma intressita ja hind2 on intressiga. Tuleks luua kaks graafikut. Need peaks olema veidi nihkes lis.
# Võiks saada vahetada.

# Ühilda ära uue koodiga, kasuta nasdaq.py (mitte vana backendi) ja tee seda nasdaq repos. Lisa siia reposse vajalikke faile juurde
# Uus muudatus see, et hoiame peaaegu (va data.py) kõik ühe faili peal. Ehk nö backend läheks ka webapp.py
# Pls kommenteeri oma faile, ma ei saa midagi aru muidu.
# Otsing nii, et saaks seda kerida. Ei oleks mingi mega pikk u know.
# (Perioodi valimine - äkki saab kuidagi teha kalendri?) - pole suurim prioriteet

#----------------------------------------------------------------------------------------#
from datetime import datetime, timedelta
import urllib.parse
import requests

# Web scraper, mis väljastab järjendi.
# Näidis json fail: https://nasdaqbaltic.com/statistics/et/instrument/EE3300002047/trading/trades_json?date=2024-09-25
def scraper(day, code):
    domain = (
        "https://nasdaqbaltic.com/statistics/et/instrument/"
        + code
        + "/trading/trades_json?"
    )
    data = {"date": day}
    url = domain + urllib.parse.urlencode(data)
    request = requests.get(url)
    result = []
    try: #kustutasin siin else osa ära, sest request.status_code tagastas 500 mitte 200
        data = request.json()
        if data["data"] != []:
            for el in data["data"]:
                clean = round(float(el["Price_clean"].replace(",", ".")), 2)
                dirty = round(float(el["Price"].replace(",", ".")), 2)
                quantity = int(el["Quantity"])
                # Päev, intressita ja intressiga hind, kogus
                result.append([day, clean, dirty, quantity])
            return result
    except ValueError:
        return None


# Muudatus - vaja väljastada iga päev mitte 9 päeva nagu LHV puhul
# get_dates(0) on täna ja get_dates(1) on eile kuni täna, ...
# Et saada viimased 7 päeva, pane get_dates(6)
def get_dates(choice):
    date_format = "%Y-%m-%d"
    from_date = datetime.now() - timedelta(days=choice)
    to_date = datetime.now()
    scrapable_dates = []
    scrapable_dates.append(from_date.strftime(date_format))

    while choice > 0:
        new_date = from_date + timedelta(days=1)
        scrapable_dates.append(new_date.strftime(date_format))
        from_date = new_date
        choice -= 1

    return scrapable_dates

'''
# Siin saab testida mitte väga populaarset võlakirja ja 100 päeva. Kõvasti aeglasem on, aga mis teha.
# Tulevikus oleks siin andmebaasi võimalus.
def test():
    päevad = get_dates(100)  # 100 päeva
    võlakiri = "EE3300002047"  # Coop Pank 5.5% bond
    kogu_info = []  # Siia salvestab kogu info
    for i in päevad:
        result = scraper(i, võlakiri)
        if result != None:  # Igaksjuhuks errorite pärast, tegin bugteste
            kogu_info += result
    print(kogu_info)


test()
'''
#----------------------------------------------------------------------------------------#

from flask import Flask, render_template, request
import data
import re

app = Flask(__name__)

def get_symbol(pattern):
    dictionary = data.database
    bond_names = []
    for key in dictionary:
        result = re.search(pattern, key, re.IGNORECASE)
        if result:
            bond_names.append(key)
    return bond_names

# Funktsioon tõlgendamaks vormist saadavad ajaperioodid sobivaks päevade arvuks get_dates() jaoks
def period_to_days(period):
    if period == "T":
        return 0
    elif period == "Y":
        return 1
    elif period == "TW":
        return 7
    elif period == "LW":
        return 14
    elif period == "TM":
        return 30
    elif period == "LM":
        return 60
    else:
        return 0

@app.route("/", methods=["GET", "POST"])
def index():
    all_symbols = list(data.database.keys())

    if request.method == "POST":
        if "symbol" in request.form:
            symbol = request.form.get("symbol") # HTML input välja sisend
            period = request.form.get("period") # HTML select välja sisend

            symbol_match = get_symbol(symbol) # Leiab sümbolile vastava info

            if symbol_match:
                bond_symbol = data.database[symbol_match[0]]
                
                # period_to_days funktsiooni kasutus
                days = period_to_days(period)
                date_list = get_dates(days)

                clean_data = []
                dirty_data = []
                for day in date_list:
                    day_trade = scraper(day, bond_symbol)
                    if day_trade:
                        # muutmine formaadiks (clean, quantity, date) / (dirty, quantity, date)
                        for trade in day_trade:
                            # trade: [kuupäev, clean_price, dirty_price, quantity]
                            clean_price = trade[1]
                            dirty_price = trade[2]
                            quantity = trade[3]
                            trade_date = trade[0]
                            clean_data.append((clean_price, quantity, trade_date))
                            dirty_data.append((dirty_price,quantity,trade_date))

                prices = clean_data # kui tahad dirty data siis vaheta siin

                if prices:
                    bond_labels = [el[2] for el in prices]
                    bond_data = [el[0] for el in prices]

                    return render_template(
                        "index.html",
                        all_symbols=all_symbols,
                        symbol_match=symbol_match,
                        prices=prices,
                        bond_labels=bond_labels,
                        bond_data=bond_data,
                    )
                
                else: # Juhul kui prices on tühi list tagastab vastava teate
                    return render_template(
                    "index.html",
                    all_symbols=all_symbols,
                    symbol_match=symbol_match,
                    message="Valitud perioodil ei toimunud ühtegi tehingut."
                    )

            else:
                # Tagastab teate kui võlakirja ei leidu
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
