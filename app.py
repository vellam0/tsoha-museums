from flask import redirect, render_template, request, url_for, session, flash
from config import app
from repositories.museum_repository \
    import get_museums, get_museum_by_id, create_museum, del_museum, edit_museum, search_museums
from repositories.review_repository import create_review, del_review, get_reviews
from repositories.user_repository import create_user, get_user, login_user


@app.route("/")
def index():
    museums = get_museums()
    return render_template("index.html", museums=museums)


@app.route("/rekisterointi", methods=["GET","POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        create_user(username, password)
        session["username"] = username
        return redirect(url_for("index"))
    return render_template("register.html")


@app.route("/kirjaudu", methods=["GET","POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        result = login_user(username, password)
        if "error" in result:
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
        address = request.form["address"]
        opening_hours = request.form["museum_hours"]
        museum_type = request.form["museum_type"]
        tags = request.form["museum_tags"]
        img_url = request.form["museum_img"]
        create_museum(name=name, 
                        bio=bio, 
                        address=address, 
                        opening_hours=opening_hours, 
                        museum_type=museum_type, 
                        tags=tags, 
                        img_url=img_url)
        return redirect("/")
    if request.method == "GET":
        return render_template("add_museum.html")


@app.route("/poista_museo/<int:museum_id>", methods=["GET", "POST"])
def delete_museum(museum_id):
    del_museum(museum_id)
    return render_template("index.html")


@app.route("/muokkaa_museota/<int:museum_id>", methods=["GET", "POST"])
def edit_museum(museum_id):
    user = get_user(session["username"])
    museum = get_museum_by_id(museum_id)

    return render_template("add_museum.html", museum=museum, is_edit=True, user=user)


@app.route("/museo/<int:museum_id>", methods=["GET", "POST"])
def show_museum(museum_id):
    username = session.get("username")
    user = get_user(username)
    user_id = user.id
    
    if request.method == "POST" and user:
        create_review(
            title=request.form["review_title"],
            review_text=request.form["review_text"],
            stars=int(request.form["stars"]),
            museum_id=museum_id,
            author_id=user_id
        )
        return redirect(url_for("show_museum", museum_id=museum_id))    
    
    reviews = get_reviews(museum_id)
    requested_museum = get_museum_by_id(museum_id)
    return render_template("museum.html", museum=requested_museum, reviews=reviews, user=user)


@app.route("/arvostelut")
def reviews():
    museums = get_museums()
    return render_template("reviews.html", museums=museums)


@app.route("/poista-arvio/<int:review_id>", methods=["GET", "POST"])
def delete_review(review_id):
    museum_id = del_review(review_id)
    return redirect(url_for('show_museum', museum_id=museum_id))


@app.route("/haku", methods=["GET", "POST"])
def search():
    content = [" "]
    if request.method == "POST":
        search_word = request.form["search_field"].strip()
        search_type = request.form.get("museum_type")
        content = search_museums(search_word, search_type)
        return render_template("search.html", content=content)
    
    return render_template("search.html", content=content)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
