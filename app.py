from flask import Flask, render_template
import requests

app = Flask(__name__)

@app.route("/")
def index():
    response = requests.get("https://fakestoreapi.com/products")
    products = response.json()
    return render_template("index.html", products=products)

if __name__ == "__main__":
    app.run(debug=True)
