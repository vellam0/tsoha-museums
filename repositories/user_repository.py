from config import db
from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy import text

def create_user(username, password):
    hashed_password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)
    sql = text("INSERT INTO users (username, password) VALUES (:username, :password)")
    db.session.execute(sql, {"username": username, "password": hashed_password})
    db.session.commit()

def login_user(username, password):
    sql = text("SELECT id, password FROM users WHERE username=:username")
    result = db.session.execute(sql, {"username": username})

    user = result.fetchone()
    if not user:
        return {"error": "Käyttäjänimeä ei löytynyt."}
    
    stored_password = user["password"]
    if not check_password_hash(stored_password, password):
        return {"error": "Salasana väärin."}
    
    return {"username": username}

def get_user(username):
    sql = text("SELECT * FROM users WHERE username=:username")
    result = db.session.execute(sql, {"username": username})
    return result.fetchone()
