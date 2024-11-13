# Loodud funktsioon ühendub LHV Balti turu veebilehega
# Ja otsib HTML-lehelt kõiki väärtpaberite nimetusi ja sümboleid

from bs4 import BeautifulSoup
import requests


def main():
    request = requests.get("https://fp.lhv.ee/market/baltic")
    soup = BeautifulSoup(request.text, "lxml")

    data = soup.find_all("a", class_=["stock-title", "stock-symbol"])

    search = "ADMB080027A"
    flag = False

    for i in range(0, len(data) - 1, 2):
        name = data[i].get_text()
        symbol = data[i + 1].get_text()

        if search in symbol:
            flag = True

        if flag:
            print(f"'{name}': '{symbol}',")


if __name__ == "__main__":
    main()
