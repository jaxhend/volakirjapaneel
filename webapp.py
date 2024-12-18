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
# VAATA ÜLE!!!
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
# LISA JUURDE!!!
################################################


from flask import Flask, render_template, request
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import urllib.parse
import requests
import data
import re


# Veebilehe kraapija, mis tagastab järjendi.
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
    try:
        if request.status_code == 200:
            data = request.json()
            if data["data"] != []:
                for el in data["data"]:
                    clean = round(float(el["Price_clean"].replace(",", ".")), 2)
                    dirty = round(float(el["Price"].replace(",", ".")), 2)
                    quantity = int(el["Quantity"])
                    result.append([day, clean, dirty, quantity])
                    # Päev, intressita ja intressiga hind, kogus
                return result
        else:
            return None
    except ValueError:
        return None


# Tagastab järjendi, milles on kuupäevad alates tänasest kuni soovitud kohani.
def get_dates(choice):
    date_format = "%Y-%m-%d"
    from_date = datetime.now() - timedelta(days=choice)
    scrapable_dates = []
    scrapable_dates.append(from_date.strftime(date_format))
    while choice > 0:
        new_date = from_date + timedelta(days=1)
        scrapable_dates.append(new_date.strftime(date_format))
        from_date = new_date
        choice -= 1
    return scrapable_dates


# Tagastab järjendi, mis sisaldab võlakirja täpsemaid andmeid
def info(code):
    url = "https://nasdaqbaltic.com/statistics/et/instrument/" + code + "/security"
    request = requests.get(url)
    soup = BeautifulSoup(request.text, "html.parser")
    td_elements = soup.find_all("td")
    result = []
    for i in range(0, len(td_elements), 2):
        result.append(
            (
                td_elements[i].text.strip().replace("\n", ""),
                td_elements[i + 1].text.strip().replace("\n", ""),
            )
        )
    return result


# Võlakirja tulusus tähtajani (YTM) kalkulaator viimase müügihinna põhjal.
# https://dqydj.com/bond-yield-to-maturity-calculator/
# choice - "5" või ""
# (seda seetõttu, kuna mõned (pankade) võlakirjad lunastatakse ennetähtaegselt ja tüüpiliselt see on 5 aastat peale noteerimist)


def YTM_calc(isin, choice=""):
    bond_info = info(isin)

    nominal = int(bond_info[1][1][:5].replace(" ", ""))
    listing_date = bond_info[3][1]
    maturity_date = bond_info[4][1]
    coupon = float(bond_info[5][1].replace(",", ""))

    # Leiame viimase müügihinna
    i = 0
    date_format = "%Y-%m-%d"
    today = datetime.now()
    while True:
        date = (today - timedelta(days=i)).strftime(date_format)
        result = scraper(date, isin)
        if result != None:
            break
        i += 1
    last_dirty_price = result[0][2]

    if choice == "5":  # Juhul kui võlakiri lunastatakse viie aasta pärast noteerimist
        formatted_date = datetime.strptime(listing_date, "%d.%m.%Y")
        matures = formatted_date.replace(year=formatted_date.year + 5)
    else:
        matures = datetime.strptime(maturity_date, "%d.%m.%Y")

    years = round((matures - today).days / 365.25, 5)

    aasta_tootlus = coupon + ((nominal - last_dirty_price * 10) / years)
    arvutus = aasta_tootlus / ((nominal + last_dirty_price * 10) / 2)
    return round(arvutus * 100, 2)


def get_symbol(pattern):
    dictionary = data.database
    bond_names = []
    for key in dictionary:
        result = re.search(pattern, key, re.IGNORECASE)
        if result:
            bond_names.append(key)
    return bond_names



app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    all_symbols = list(data.database.keys())

    if request.method == "POST":
        if "symbol" in request.form:
            symbol = request.form.get("symbol")  # HTML input välja sisend
            period = request.form.get("period")  # HTML select välja sisend

            symbol_match = get_symbol(symbol)  # Leiab sümbolile vastava info

            if symbol_match:
                bond_symbol = data.database[symbol_match[0]]

                
                date_list = get_dates(int(period))

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
                            dirty_data.append((dirty_price, quantity, trade_date))

                prices = clean_data  # kui tahad dirty data siis vaheta siin

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

                else:  # Juhul kui prices on tühi list tagastab vastava teate
                    return render_template(
                        "index.html",
                        all_symbols=all_symbols,
                        symbol_match=symbol_match,
                        message="Valitud perioodil ei toimunud ühtegi tehingut.",
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
        "index.html", all_symbols=all_symbols
    )


if __name__ == "__main__":
    app.run(debug=True)
