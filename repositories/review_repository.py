from config import db
from sqlalchemy import text
from datetime import date, datetime


def create_review(title, review_text, stars, museum_id, author_id):
    now = datetime.now().strftime("%d-%m-%Y %H:%M")
    sql = text("""INSERT INTo reviews (title, review_text, stars, date, museum_id, author_id)
               VALUES (:title, :review_text, :stars, :date, :museum_id, :author_id)""")
    db.session.execute(sql, {
        "title": title,
        "review_text": review_text,
        "stars": stars,
        "date": now,
        "museum_id": museum_id,
        "author_id": author_id
    })
    db.session.commit()

def del_review(review_id):
    sql = text("SELECT museum_id FROM reviews WHERE id=:review_id")
    result = db.session.execute(sql, {"review_id":review_id})
    museum_id = result.fetchone()[0]
    sql_delete_review = text("DELETE FROM reviews WHERE id=:review_id")
    db.session.execute(sql_delete_review, {"review_id":review_id})
    db.session.commit()
    return museum_id

def get_reviews(museum_id):
    sql = text("""SELECT 
            reviews.id, 
            reviews.title, 
            reviews.review_text, 
            reviews.stars, 
            reviews.date, 
            reviews.museum_id, 
            reviews.author_id, 
            users.username
            FROM reviews
            JOIN users ON reviews.author_id = users.id
            WHERE reviews.museum_id=:museum_id""")
    result = db.session.execute(sql, {"museum_id":museum_id})
    reviews = result.fetchall()
    return reviews
