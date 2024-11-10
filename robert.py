import backend

from flask import Flask
app = Flask(__name__)
@app.route("/")
def hello_world():
    backend.main()
    return "Hello World"

if __name__ == '__main__':
    app.run()
