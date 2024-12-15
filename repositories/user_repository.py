from config import db
from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy import text


def create_user(username, password):
    hashed_password = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)
    sql = text("INSERT INTO users (username, password) VALUES (:username, :password) RETURNING id")
    result = db.session.execute(sql, {"username": username, "password": hashed_password})
    db.session.commit()
    return result.fetchone()[0]


def login_user(username, password):
    sql = text("SELECT id, password FROM users WHERE username=:username")
    result = db.session.execute(sql, {"username": username})

    user = result.fetchone()
    if not user:
        return {"error": "Käyttäjänimeä ei löytynyt."}

    stored_password = user.password
    if not check_password_hash(stored_password, password):
        return {"error": "Salasana väärin."}

    return {"username": username, "user_id": user.id}


def delete_user(user_id):
    sql = text("DELETE FROM users WHERE id = :user_id")
    db.session.execute(sql, {"user_id": user_id})
    db.session.commit()


def get_user(username):
    sql = text("SELECT id, username FROM users WHERE username=:username")
    result = db.session.execute(sql, {"username": username})
    return result.fetchone()


def get_user_roles(user_id):
    sql = text("SELECT r.role_name FROM roles r INNER JOIN user_roles ur ON r.id = ur.role_id WHERE ur.user_id = :user_id")
    result = db.session.execute(sql, {"user_id": user_id}).fetchall()
    return [row.role_name for row in result]


def add_user_role(user_id, role_name):
    result = db.session.execute(text("SELECT id FROM roles WHERE role_name = :role_name"),{"role_name": role_name}).fetchone()
    role_id = result[0]
    sql = text("INSERT INTO user_roles (user_id, role_id) VALUES (:user_id, :role_id)")
    db.session.execute(sql, {"user_id": user_id, "role_id": role_id})
    db.session.commit()
