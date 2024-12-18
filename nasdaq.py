# Mina lisan juurde:
# YTM kalkulaator
# data.py

# Robert:
# Juurde lisada tee ilusaks, kommenteeri koodi, kasutu lõika välja, II graafik, info ja YTM calc.

from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import urllib.parse
import requests


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
                return result
        else:
            return None
    except ValueError:
        return None


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


# Siin saab testida mitte väga populaarset võlakirja ja 100 päeva. Kõvasti aeglasem on, aga mis teha.
# Tulevikus oleks siin andmebaasi võimalus.
def test():

    päevad = get_dates(50)  # 100 päeva
    võlakiri = "EE1300001563"  # Coop Pank 5.5% bond
    kogu_info = []  # Siia salvestab kogu info
    for i in päevad:
        result = scraper(i, võlakiri)
        if result != None:  # Igaksjuhuks errorite pärast, tegin bugteste
            kogu_info += result
    print(info(võlakiri))
    print(kogu_info)


# Bond Yield to Maturity (YTM) Calculator
# Viide: https://dqydj.com/bond-yield-to-maturity-calculator/
# Ostuhind on viimane müügihind


def calc(aastad, isin="EE3300003573"):
    teave = info(isin)
    nominaal = int(teave[1][1][:5].replace(" ", ""))
    kupong = float(teave[5][1].replace(",", ""))

    i = 0
    date_format = "%Y-%m-%d"
    täna = datetime.now()
    while True:
        from_date = täna - timedelta(days=i)
        kuupäev = from_date.strftime(date_format)

        vastus = scraper(kuupäev, isin)
        if vastus != None:
            break
        i += 1
    ostuhind = vastus[0][2]

    lunastus = teave[4][1]
    kestab = datetime.strptime(lunastus, "%d.%m.%Y")

    aastad = round((kestab - täna).days / 365.25, 5)


def calc(aastad, isin="EE3300003573"):
    teave = info(isin)
    nominaal = int(teave[1][1][:5].replace(" ", ""))
    kupong = float(teave[5][1].replace(",", ""))

    i = 0
    date_format = "%Y-%m-%d"
    täna = datetime.now()
    while True:
        from_date = täna - timedelta(days=i)
        kuupäev = from_date.strftime(date_format)

        vastus = scraper(kuupäev, isin)
        if vastus != None:
            break
        i += 1
    ostuhind = vastus[0][2]

    lunastus = teave[4][1]
    kestab = datetime.strptime(lunastus, "%d.%m.%Y")

    aastad = round((kestab - täna).days / 365.25, 5)
    aasta_tootlus = kupong + ((nominaal - ostuhind) / aastad)
    arvutus = aasta_tootlus / ((nominaal + ostuhind) / 2)
    print(round(arvutus * 100, 2))

    print(round(arvutus * 100, 2))


kupong = 105
nominaal = 1000
aastad = 8.8
ostuhind = 1200


aasta_tootlus = kupong + ((nominaal - ostuhind) / aastad)
arvutus = aasta_tootlus / ((nominaal + ostuhind) / 2)
print(aasta_tootlus)
print(aasta_tootlus)
