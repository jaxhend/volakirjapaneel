print("Hello World")
for i in range(10):
    print(str(i) + " Hello world")

#virtualenv 20.27.0

#Flask version 3.0.3
from flask import Flask
app = Flask(__name__)
@app.route("/")
def hello_world():
    return "Hello World"

if __name__ == '__main__':
    app.run()
"""
#debug function
app.debug=True
app.run()
app.run(debug=True)

#externally visible server
app.run(host='0.0.0.0')
"""