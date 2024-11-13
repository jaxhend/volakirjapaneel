#pip install virtualenv
#pip install flask
#python frontend_flask.py

"""
references:
https://medium.com/@moraneus/python-flask-a-comprehensive-guide-from-basic-to-advanced-fbc6ec9aa5f7
"""

from flask import Flask, render_template, request
import backend

app = Flask(__name__)

@app.route('/',methods=['GET','POST'])
def index():
    data = {}

    if request.method == 'POST':
        symbol = request.form.get('symbol')
        period = request.form.get('period')
        
        bond_code = backend.get_symbol(symbol)
        if not bond_code:
            data['error'] = "Bond not found. Try again."
        else:
            dates = backend.get_dates(period)
            trades = backend.main(bond_code, dates)
            average_price = round(sum(float(trade[0]) for trade in trades) / len(trades), 2) if trades else None

            data = {
                'trades': trades,
                'average_price': average_price,
                'period': period,
                'bond_code': bond_code
            }
        return render_template('symbol_data.html',data=data)
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
