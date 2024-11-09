from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import urllib.parse
import requests


def get_symbol():
    # siia lisame võlakirja nimi ja sümboli andmebaasi
    user_symbol = input("Sisesta võlakirja sümbol: ") # ajutiselt väljaspool vigu
    return None


def get_dates():
    date_format = "%d.%m.%Y"
    today = datetime.now()

    print("-----------------------Speeddial-----------------------")
    print("Today - T")
    print("Yesterday - Y")
    print("This week- TW")
    print("Last week - LW")
    print("This month - TM")
    print("Last month - LM")
    print("Press ENTER if you want to choose specific dates.")
    choice = input().upper()
    
    if choice == "T":
        formatted_date_from = today
        formatted_date_end = today
   
    elif choice == "Y": 
        formatted_date_from = datetime.now() - timedelta(days=1)
        formatted_date_end = datetime.now() - timedelta(days=1)
    
    elif choice == "TW":
        monday = today - timedelta(days=today.weekday())
        formatted_date_from = monday
        formatted_date_end = today

    elif choice == "LW":
        last_monday = today - timedelta(days=today.weekday() + 7)
        last_friday = last_monday + timedelta(days=4)
        formatted_date_from = last_monday
        formatted_date_end = last_friday

    elif choice == "TM":
        first_day = today.replace(day=1)
        formatted_date_from = first_day
        formatted_date_end = today
    
    elif choice == "LM":
        first_day_this_month = today.replace(day=1)
        last_day_last_month = first_day_this_month - timedelta(days=1)
        first_day_last_month = last_day_last_month.replace(day=1)
        formatted_date_from = first_day_last_month
        formatted_date_end = last_day_last_month
    
    else:
        while True:
            try:
                user_date_from = input("Tehingud alates (formaadis dd.mm.yy): ").strip()
                user_date_end = input("Tehingud kuni (formaadis dd.mm.yy): ").strip()
                formatted_date_from = datetime.strptime(user_date_from, date_format)
                formatted_date_end = datetime.strptime(user_date_end, date_format)
                break
            except ValueError:
                print("Proovi uuesti")

        if formatted_date_end > today:
            formatted_date_end = today
            return [formatted_date_from, formatted_date_end]

    difference = formatted_date_end - formatted_date_from
    day_difference = difference.days
    scrapable_dates = []
    scrapable_dates.append(formatted_date_from.strftime(date_format))

    if day_difference >= 9:
        new_date = formatted_date_from + timedelta(days=9)
        scrapable_dates.append(new_date.strftime(date_format))
        day_difference -= 9
        
        while new_date + timedelta(days=9) < formatted_date_end:
            new_date = new_date + timedelta(days=9)
            scrapable_dates.append(new_date.strftime(date_format))
        
        if new_date < formatted_date_end:
            scrapable_dates.append(formatted_date_end.strftime(date_format))
    
    else:
        scrapable_dates.append(formatted_date_end.strftime(date_format))
    return scrapable_dates


def main():
    dates = get_dates()
    user_symbol = "BIGB080033B"

    if len(dates) > 2:
        pass

    for i in range(len(dates)-1):
        data = {
            "symbol": user_symbol,
            "date": dates[i] + " - " + dates[i+1]
        }

        domain = "https://fp.lhv.ee/market/balticTrades?"
        url = domain + urllib.parse.urlencode(data)
        request = requests.get(url)
        soup  = BeautifulSoup(request.content, 'lxml')

        table = soup.find('table')
        trades = []
        td_elements = []

        for row in reversed(table.find_all("td")):
            td_elements += [row.get_text()]
        for i in range(2, len(td_elements), 6):
            trades.append((td_elements[i+1], td_elements[i], td_elements[i+3][:10]))

        print(trades)

if __name__ == "__main__":
    main()