from flask import Flask, render_template, url_for, g, session  # 添加 url_for 导入, request, redirect, url_for, session, g, flash
import json
import os
from db import load_users, add_user, find_user # 引入 db.py 中的函數

app = Flask(__name__)
app.secret_key = 'your_super_secret_key' # 在生產環境中請使用更安全的密鑰

PRODUCTS_FILE = 'fake_store_data.json'

def load_products():
    """從 JSON 檔案載入商品資料"""
    try:
        with open(PRODUCTS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: {PRODUCTS_FILE} not found.")
        return []

@app.before_request
def load_logged_in_user():
    """在每個請求之前載入登入用戶資訊"""
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        # 在這裡，我們簡化地從 users.json 中查找用戶，
        # 實際應用中會從資料庫中查找
        users = load_users()
        g.user = next((u for u in users if u['username'] == user_id), None)

@app.route("/")
def index():
    """首頁路由"""
    # 這裡我們只顯示產品列表，首頁和列表頁可以共用或分開
    banner_image = url_for('static', filename='images/banner.jpg')
    products = load_products()
    return render_template('index.html', 
                         banner_image=banner_image,
                         products=products)

@app.route("/products")
def products_list():
    """商品列表頁路由"""
    products = load_products()
    return render_template("index.html", products=products) # 仍使用 index.html 顯示列表

@app.route("/product/<int:product_id>")
def product_detail(product_id):
    """產品詳情頁路由"""
    products = load_products()
    product = next((p for p in products if p['id'] == product_id), None)
    if product is None:
        flash("商品不存在！", "error")
        return redirect(url_for('products_list'))
    return render_template("product.html", product=product)

@app.route("/register", methods=["GET", "POST"])
def register():
    """註冊功能路由"""
    if g.user:
        return redirect(url_for('index')) # 如果已登入，則導向首頁

    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        error = None

        if not username:
            error = "用戶名為必填。"
        elif not password:
            error = "密碼為必填。"
        elif add_user(username, password):
            flash("註冊成功，請登入！", "success")
            return redirect(url_for('login'))
        else:
            error = "用戶名已存在。"
        flash(error, "error") # 顯示錯誤訊息
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """登入功能路由"""
    if g.user:
        return redirect(url_for('index')) # 如果已登入，則導向首頁

    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        error = None
        user = find_user(username, password)

        if user is None:
            error = "用戶名或密碼不正確。"
        else:
            session['user_id'] = user['username'] # 將用戶名儲存到 session 中
            flash("登入成功！", "success")
            return redirect(url_for('index'))
        flash(error, "error") # 顯示錯誤訊息
    return render_template("login.html")

@app.route("/logout")
def logout():
    """登出功能路由"""
    session.pop('user_id', None)
    flash("您已登出。", "info")
    return redirect(url_for('index'))

@app.route("/add_to_cart/<int:product_id>", methods=["POST"])
def add_to_cart(product_id):
    """加入購物車功能"""
    if not g.user:
        flash("請先登入才能加入購物車！", "warning")
        return redirect(url_for('login'))

    products = load_products()
    product = next((p for p in products if p['id'] == product_id), None)

    if product:
        cart = session.get('cart', {})
        product_id_str = str(product_id) # 將 product_id 轉為字串作為 key

        if product_id_str in cart:
            cart[product_id_str]['quantity'] += 1
        else:
            cart[product_id_str] = {
                'id': product['id'],
                'title': product['title'],
                'price': product['price'],
                'image': product['image'],
                'quantity': 1
            }
        session['cart'] = cart
        flash(f"已將 {product['title']} 加入購物車！", "success")
    else:
        flash("商品不存在，無法加入購物車。", "error")
    return redirect(url_for('cart'))

@app.route("/remove_from_cart/<int:product_id>", methods=["POST"])
def remove_from_cart(product_id):
    """從購物車移除商品功能"""
    if not g.user:
        flash("請先登入才能操作購物車！", "warning")
        return redirect(url_for('login'))

    cart = session.get('cart', {})
    product_id_str = str(product_id)

    if product_id_str in cart:
        if cart[product_id_str]['quantity'] > 1:
            cart[product_id_str]['quantity'] -= 1
        else:
            del cart[product_id_str]
        session['cart'] = cart
        flash("商品已從購物車移除！", "info")
    else:
        flash("購物車中沒有此商品。", "error")
    return redirect(url_for('cart'))

@app.route("/cart")
def cart():
    """購物車頁面路由"""
    if not g.user:
        flash("請先登入才能查看購物車！", "warning")
        return redirect(url_for('login'))

    cart_items = session.get('cart', {}).values()
    total_price = sum(item['price'] * item['quantity'] for item in cart_items)
    return render_template("cart.html", cart_items=cart_items, total_price=total_price)

@app.route("/checkout")
def checkout():
    """結帳頁面路由"""
    if not g.user:
        flash("請先登入才能進行結帳！", "warning")
        return redirect(url_for('login'))

    cart_items = session.get('cart', {}).values()
    if not cart_items:
        flash("購物車是空的，無法結帳。", "warning")
        return redirect(url_for('products_list'))

    total_price = sum(item['price'] * item['quantity'] for item in cart_items)
    return render_template("checkout.html", cart_items=cart_items, total_price=total_price)

@app.route("/place_order", methods=["POST"])
def place_order():
    """確認訂單 (模擬)"""
    if not g.user:
        flash("請先登入才能下訂單！", "warning")
        return redirect(url_for('login'))

    cart_items = session.get('cart', {}).values()
    if not cart_items:
        flash("購物車是空的，無法下訂單。", "warning")
        return redirect(url_for('products_list'))

    # 這裡可以處理收件資訊，例如儲存到資料庫
    name = request.form['name']
    address = request.form['address']
    phone = request.form['phone']

    # 模擬訂單處理
    print(f"新訂單來自：{g.user['username']}")
    print(f"收件人：{name}, 地址：{address}, 電話：{phone}")
    print("訂單內容：")
    for item in cart_items:
        print(f"- {item['title']} x {item['quantity']} (${item['price'] * item['quantity']})")

    session.pop('cart', None) # 清空購物車
    flash("訂單已成功送出！", "success")
    return redirect(url_for('order_success'))

@app.route("/order_success")
def order_success():
    """訂單成功頁面"""
    return render_template("order_success.html")

if __name__ == "__main__":
    # 確保 data 目錄存在
    if not os.path.exists('data'):
        os.makedirs('data')
    # 如果 products.json 不存在，從 fake_store_api 獲取資料

    app.run(debug=True)