from flask import Flask, render_template

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("fetch_test.html")


@app.route("/fetch")
def fetch():
    return {"message": "Hello, World!"}


app.run(debug=True)
