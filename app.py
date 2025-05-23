from flask import Flask, render_template
import json
import os
import requests

def load_products():
    with open('fake_store_data.json', 'r', encoding='utf-8') as f:
        return json.load(f)

app = Flask(__name__)

@app.route("/")
def index():
    products = load_products()
    return render_template("index.html", products=products)

if __name__ == "__main__":
    app.run(debug=True)
# def index():
#     response = requests.get("https://fakestoreapi.com/products")
#     print(response.json())
#     products = response.json()
#     return render_template("index.html", products=products)

# if __name__ == "__main__":
#     app.run(debug=True)