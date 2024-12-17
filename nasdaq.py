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
    try:
        if request.status_code == 200:
            data = request.json()
            if data["data"] != []:
                for el in data["data"]:
                    clean = round(float(el["Price_clean"].replace(",", ".")), 2)
                    dirty = round(float(el["Price"].replace(",", ".")), 2)
                    quantity = int(el["Quantity"])
                    # Päev, intressita ja intressiga hind, kogus
                    result.append([day, clean, dirty, quantity])
                return result
        else:
            return None
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
