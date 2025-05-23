from flask import Flask, render_template, url_for  # 添加 url_for 导入
import json
import os
import requests

def load_products():
    with open('fake_store_data.json', 'r', encoding='utf-8') as f:
        return json.load(f)

app = Flask(__name__)

@app.route("/")
def index():
    banner_image = url_for('static', filename='images/banner.jpg')
    products = load_products()
    return render_template('index.html', 
                         banner_image=banner_image,
                         products=products)

if __name__ == "__main__":
    app.run(debug=True)