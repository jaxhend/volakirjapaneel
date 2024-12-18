from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import urllib.parse
import requests

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

def YTM_calc(isin, choice = ""):
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

    if choice == "5": # Juhul kui võlakiri lunastatakse viie aasta pärast noteerimist
        formatted_date = datetime.strptime(listing_date, "%d.%m.%Y")
        matures = formatted_date.replace(year=formatted_date.year + 5)
    else:
        matures = datetime.strptime(maturity_date, "%d.%m.%Y")

    years = round((matures - today).days / 365.25, 5)

    aasta_tootlus = coupon + ((nominal - last_dirty_price * 10) / years)
    arvutus = aasta_tootlus / ((nominal + last_dirty_price * 10) / 2)
    return round(arvutus * 100, 2)


# Testime
def main():
    päevad = get_dates(50)  # 50 päeva
    võlakiri = "EE3300003573"  # LHV Group 10.5% subord. bond
    tehingud = []
    for i in päevad:
        result = scraper(i, võlakiri)
        if result != None:
            tehingud += result
    print(info(võlakiri))
    print(YTM_calc(võlakiri, '5'), "%")
    for el in tehingud:
        print(el)

if __name__ == "__main__":
    main()