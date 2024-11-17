
from datetime import date, datetime
from flask import Flask
from flask import redirect, render_template, request, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_
from os import getenv
from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy.orm import relationship

    # session["csrf_token"] = secrets.token_hex(16)

today = date.today()

app = Flask(__name__)
app.secret_key = getenv("SECRET_KEY")
db_password = getenv("DB_KEY")

app.config["SQLALCHEMY_DATABASE_URI"] = f"postgresql://postgres:{db_password}@localhost:5432/museosovellus"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

    reviews = relationship("Review", back_populates="review_author")


class Museum(db.Model):
    __tablename__ = "museums"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    bio = db.Column(db.Text, nullable=False)
    opening_hours = db.Column(db.String(1000), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    museum_type = db.Column(db.String(250), nullable=False)
    tags = db.Column(db.String(250))
    img_url = db.Column(db.String(250))

    reviews = relationship("Review", back_populates="parent_museum")


class Review(db.Model):
    __tablename__ = "reviews"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text, nullable=False)
    text = db.Column(db.Text, nullable=False)
    stars = db.Column(db.Integer, nullable=False)
    date = datetime.now().strftime("%d-%m-%Y %H:%M")

    museum_id = db.Column(db.Integer, db.ForeignKey("museums.id"))
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    parent_museum = relationship("Museum", back_populates="reviews")
    review_author = relationship("User", back_populates="reviews")



with app.app_context():
    db.create_all()

@app.route("/")
def index():
    museums = Museum.query.all()
    return render_template("index.html", museums=museums)

@app.route("/rekisterointi", methods=["GET","POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        print(f"Lomakkeen tiedot: {username}, {password}")

        if User.query.filter_by(username=username).first():
            flash("Käyttäjänimi on jo käytössä!")
            return redirect(url_for("register"))
        
        new_user = User(
            username=username,
            password=generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)
        )
        try:
            db.session.add(new_user)
            db.session.commit()
            session["username"] = username
            flash("Käyttäjä luotu onnistuneesti!")
            print("käyttäjä luotu")
            return redirect(url_for("index"))
        except Exception as e:
            db.session.rollback()
            flash("Rekisteröinnissä tapahtui virhe.")
            print(f"Virhe: {e}")
            return redirect(url_for("register"))

    return render_template("register.html")

@app.route("/kirjaudu", methods=["GET","POST"])
def login():
    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username=username).first()

        if not user:
            flash("Käyttäjänimeä ei löytynyt, kokeile uudestaan.")
            return redirect(url_for("login"))
        elif not check_password_hash(user.password, password):
            print("Salasana ei täsmää")
            flash("Salasana väärin, kokeile uudestaan.")
            return redirect(url_for("login"))
        else:
            session["username"] = username
            return redirect("/")
        
    return render_template("login.html")

@app.route("/kirjaudu_ulos")
def logout():
    del session["username"]
    return redirect("/")

@app.route("/lisaa_museo", methods=["GET", "POST"])
def add_museum():
    if request.method == "POST":
        name = request.form["museum_name"]
        bio = request.form["museum_bio"]
        hours = request.form["museum_hours"]
        museum_type = request.form["museum_type"]
        tags = request.form["museum_tags"]
        latitude = request.form["latitude"]
        longitude = request.form["longitude"]
        img_url = request.form["museum_img"]

        new_museum = Museum(
            name = name,
            bio = bio,
            opening_hours = hours,
            latitude = float(latitude),
            longitude = float(longitude),
            museum_type = museum_type,
            tags = tags if tags else None,
            img_url = img_url if img_url else None
        )
        db.session.add(new_museum)
        db.session.commit()
        flash("Museo lisätty onnistuneesti!")
        print("MUSEO LISÄTTY\n\n\nMUSEO LISÄTTY")
        return redirect("/")

    return render_template("add_museum.html")

@app.route("/poista_museo", methods=["GET", "POST"])
def delete_museum():
    return render_template("index.html")

@app.route("/muokkaa_museota/<int:museum_id>", methods=["GET", "POST"])
def edit_museum(museum_id):
    user = User.query.filter_by(username=session["username"]).first()
    museum = Museum.query.get(museum_id)
    return render_template("add_museum.html", museum=museum, is_edit=True, user=user)

@app.route("/museo/<int:museum_id>", methods=["GET", "POST"])
def show_museum(museum_id):
    user = None
    if "username" in session:
        user = User.query.filter_by(username=session["username"]).first()

    requested_museum = Museum.query.get(museum_id)

    if request.method == "POST":
        if not user:
            flash("Kirjaudu sisään, että voit kirjoittaa arvion.")
            return render_template("museum.html", museum=requested_museum, user=user)
        new_review = Review(
        title = request.form["review_title"],
        text = request.form["review_text"],
        stars = request.form["stars"],
        museum_id = museum_id,
        author_id = user.id
        )
        db.session.add(new_review)
        print("arvio lisätty")
        db.session.commit()
        return redirect(url_for("show_museum", museum_id=museum_id, user=user))


    return render_template("museum.html", museum=requested_museum, user=user)

@app.route("/arvostelut")
def reviews():
    museums = Museum.query.all()
    return render_template("reviews.html", museums=museums)

@app.route("/poista-arvio/<int:review_id>", methods=["GET", "POST"])
def delete_review(review_id):
    review_to_delete = Review.query.get(review_id)
    review_source = review_to_delete.parent_museum.id
    db.session.delete(review_to_delete)
    db.session.commit()
    return redirect(url_for('show_museum', museum_id=review_source))

@app.route("/haku", methods=["GET", "POST"])
def search():
    content = [" "]
    if request.method == "POST":
        search_word = request.form["search_field"].strip()
        search_types = request.form.getlist("museum_type")
        filters = []

        if search_word:
            filters.append(Museum.name.like('%' + search_word + '%'))
            filters.append(Museum.tags.like('%' + search_word + '%'))

        if search_types:
            filters.append(Museum.museum_type.in_(search_types))

        if filters:
            content = Museum.query.filter(or_(*filters)).all()

        return render_template("search.html", content=content)
    return render_template("search.html", content=content)

if __name__ == "__main__":
    app.run(debug=True)

