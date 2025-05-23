import json

USERS_FILE = 'users.json'

def load_users():
    """載入所有用戶資料"""
    try:
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

def save_users(users):
    """儲存用戶資料"""
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(users, f, indent=2, ensure_ascii=False)

def add_user(username, password):
    """新增用戶"""
    users = load_users()
    if any(u['username'] == username for u in users):
        return False # 用戶已存在
    users.append({"username": username, "password": password})
    save_users(users)
    return True

def find_user(username, password):
    """查找用戶"""
    users = load_users()
    for user in users:
        if user['username'] == username and user['password'] == password:
            return user
    return None