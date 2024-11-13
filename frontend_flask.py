from flask import Flask, render_template, request, session
import random

from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import urllib.parse
import requests
import data
import re
import backend

#https://flask.palletsprojects.com/en/stable/quickstart/#sessions

def get_symbol(pattern):
    dictionary = data.database
    while True:
        bond_names = []
        for key in dictionary:
            result = re.search(pattern, key, re.IGNORECASE)
            if result:
                bond_names += [key]
        return bond_names



app = Flask(__name__)
app.secret_key = "robertijahendrikuprojekt"

@app.route('/',methods=['GET','POST'])
def index():
    sõna = session.get('sõna', None)
    time = session.get('time', None)
    
    if request.method == 'POST':
        if 'symbol' in request.form:
            symbol = request.form.get('symbol')
            aeg = request.form.get('period')
            sõna = get_symbol(symbol)
            time = backend.get_dates(aeg) # sellega korras

            session['sõna'] = sõna
            session['time'] = time
            return render_template('index.html', sõna=sõna)

        elif 'number' in request.form:
            number = request.form.get('number') 
            võlakiri = sõna[int(number)-1]

            dictionary = data.database
            if võlakiri in dictionary:
                value = dictionary[võlakiri]

            prices = backend.main(value, time)

            return render_template('index.html', bond1 = prices) 
    else:
        return render_template('index.html')
    
    return render_template('index.html', sõna=sõna)

if __name__ == '__main__':
    app.run(debug=True)
