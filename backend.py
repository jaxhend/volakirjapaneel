# The script asks the user for the name of the bond and time.
# The script then outputs the transactions within that time.

# Pean muutma nii, et ei oleks ühtegi print funktsiooni. Funktsioonid ise peaksid ainult tagastama.


from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import urllib.parse
import requests
import data
import re


def get_symbol(pattern):
    dictionary = data.database
    while True:
        bond_names = []
        for key in dictionary.keys():
            result = re.search(pattern, key, re.IGNORECASE)
            if result:
                bond_names += [key]

        if bond_names == []:
            print("Try again")
            return None

        for i in range(len(bond_names)):
            print(f"{i+1}. {bond_names[i]}")

        choice = input(
            "Choose a bond with the corresponding number or write X and search again: "
        )

        try:
            if bond_names[int(choice) - 1] in dictionary:
                return dictionary[bond_names[int(choice) - 1]]
        except:
            print("Try again")
            return None


def get_dates(value=""):
    date_format = "%d.%m.%Y"
    today = datetime.now()

    if value == "":
        print("-----------------------Speeddial-----------------------")
        print("Today - T")
        print("Yesterday - Y")
        print("This week- TW")
        print("Last week - LW")
        print("This month - TM")
        print("Last month - LM")
        choice = input("Press ENTER if you want to choose specific dates: ").upper()
    else:
        choice = value

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
                user_date_from = input("Transactions from (dd.mm.yyyy): ").strip()
                user_date_end = input("Transactions till (dd.mm.yyyy): ").strip()
                formatted_date_from = datetime.strptime(user_date_from, date_format)
                formatted_date_end = datetime.strptime(user_date_end, date_format)
                break
            except ValueError:
                print("Proovi uuesti")

        if formatted_date_end > today:
            formatted_date_end = today

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


def main(user_symbol="", dates=""):
    domain = "https://fp.lhv.ee/market/balticTrades?"
    trades = []
    if user_symbol == "":
        while True:
            search_pattern = input(
                "Search for a bond or press ENTER to see all bonds: "
            )
            user_symbol = get_symbol(search_pattern)
            if user_symbol != None:
                break

    if dates == "":
        dates = get_dates()

    for i in range(len(dates) - 1):
        data = {"symbol": user_symbol, "date": dates[i] + " - " + dates[i + 1]}

        url = domain + urllib.parse.urlencode(data)
        request = requests.get(url)
        soup = BeautifulSoup(request.text, "html.parser")

        table = soup.find("table")
        td_elements = []

        for row in reversed(table.find_all("td")):
            td_elements += [row.get_text()]
        for i in range(2, len(td_elements), 6):
            trades.append((td_elements[i + 1], td_elements[i], td_elements[i + 3][:10]))

    print(trades)

    sum = 0
    for j in range(len(trades)):
        sum += float(trades[j][0])
        average = round(sum / len(trades), 2)
    print(f"Average price is {average}")


if __name__ == "__main__":
    main()
