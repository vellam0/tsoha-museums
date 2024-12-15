from flask import redirect, render_template, request, url_for, session, jsonify
from datetime import datetime
from functools import wraps
from config import app
from repositories.museum_repository \
    import get_museums, get_museum_by_id, create_museum, del_museum, update_museum, search_museums
from repositories.review_repository import create_review, del_review, get_reviews, get_all_reviews, get_average_stars_for_all_museums
from repositories.user_repository import create_user, get_user, login_user, get_user_roles, add_user_role, delete_user
from repositories.location_repository import update_locations_from_museums, get_map_details
from util import validate_login_info, validate_review_form, validate_museum_form


@app.before_first_request
def update_locations_automatically():
    update_locations_from_museums()


@app.template_filter("format_date")
def format_date(value):
    try:
        return datetime.strptime(value, "%d-%m-%Y %H:%M").strftime("%d.%m.%Y klo %H:%M")
    except (ValueError, TypeError):
        return value


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_roles = get_user_roles(session.get("user_id"))
        if "admin" not in user_roles:
            return redirect("/")
        return f(*args, **kwargs)
    return decorated_function


@app.before_request
def verify_csrf_token():
    if request.method == "POST" and request.endpoint not in ["search"]:
        if session["csrf_token"] != request.form["csrf_token"]:
            return "Invalid csrf_token", 403


@app.route("/")
def index():
    museums = get_museums()
    reviews = get_all_reviews()
    return render_template("index.html", museums=museums, reviews=reviews)


@app.route("/rekisterointi", methods=["GET","POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        confirm_password = request.form["confirm_password"]
        is_admin = "is_admin" in request.form

        existing_user = get_user(username)
        if existing_user:
            return render_template("register.html", error="Käyttäjänimi on jo käytössä.")

        error = validate_login_info(username, password, confirm_password)
        if error:
            return render_template("register.html", error=error)

        user_id = create_user(username, password)
        if is_admin:
            add_user_role(user_id, "admin")
        else:
            add_user_role(user_id, "user")

        session["user_id"] = user_id
        session["username"] = username
        session["user_roles"] = ["admin"] if is_admin else ["user"]
        return redirect(url_for("index"))
    return render_template("register.html")


@app.route("/kirjaudu", methods=["GET","POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        result = login_user(username, password)
        if "error" in result:
            return render_template("login.html", error=result["error"])
        else:
            session["username"] = username
            session["user_roles"] = get_user_roles(result["user_id"])
            return redirect("/")
        
    return render_template("login.html")


@app.route("/kirjaudu_ulos")
def logout():
    del session["username"]
    return redirect("/")


@app.route("/lisaa_museo", methods=["GET", "POST"])
def add_museum():
    if request.method == "POST":
        name = request.form.get("museum_name", "")
        bio = request.form.get("museum_bio", "")
        address = request.form.get("address", "")
        opening_hours = request.form.get("museum_hours", "")
        museum_type = request.form.get("museum_type", "")
        tags = request.form.get("museum_tags")
        img_url = request.form.get("museum_img")

        error = validate_museum_form(name, bio, address, opening_hours, museum_type, tags, img_url)
        if error:
            return render_template("add_museum.html", error=error, form=request.form)
        create_museum(name=name, 
                        bio=bio, 
                        address=address, 
                        opening_hours=opening_hours, 
                        museum_type=museum_type, 
                        tags=tags, 
                        img_url=img_url)
        return redirect("/")
    if request.method == "GET":
        return render_template("add_museum.html", form={})


@app.route("/poista_museo/<int:museum_id>", methods=["GET", "POST"])
@admin_required
def delete_museum(museum_id):
    del_museum(museum_id)
    return redirect("/")


@app.route("/muokkaa_museota/<int:museum_id>", methods=["GET", "POST"])
def edit_museum(museum_id):
    user = get_user(session["username"])
    museum = get_museum_by_id(museum_id)
    reviews = get_reviews(museum_id)

    if request.method == "POST":
        name = request.form["museum_name"]
        bio = request.form["museum_bio"]
        address = request.form["address"]
        opening_hours = request.form["museum_hours"]
        museum_type = request.form["museum_type"]
        tags = request.form["museum_tags"]
        img_url = request.form["museum_img"]

        error = validate_museum_form(name, bio, address, opening_hours, tags, img_url, edit_id=museum_id)
        if error:
            return render_template("add_museum.html", museum=museum, is_edit=True, error=error)
        update_museum(museum_id, name, bio, address, opening_hours, museum_type, tags, img_url)

        museum = get_museum_by_id(museum_id)
        return render_template("museum.html", museum=museum, reviews=reviews, user=user)
    
    if request.method == "GET":
        return render_template("add_museum.html", museum=museum, is_edit=True, user=user)
    return redirect("/")


@app.route("/museo/<int:museum_id>", methods=["GET", "POST"])
def show_museum(museum_id):
    username = session.get("username")
    user = get_user(username)
    reviews = get_reviews(museum_id)
    requested_museum = get_museum_by_id(museum_id)    

    if request.method == "POST" and user:
        user_id = user.id

        error = validate_review_form(
            title=request.form["review_title"],
            review_text=request.form["review_text"])
        if error:
            return render_template("museum.html", museum=requested_museum, reviews=reviews, user=user, error=error)

        create_review(
            title=request.form["review_title"],
            review_text=request.form["review_text"],
            stars=int(request.form["stars"]),
            museum_id=museum_id,
            author_id=user_id
        )
        return redirect(url_for("show_museum", museum_id=museum_id))    
    return render_template("museum.html", museum=requested_museum, reviews=reviews, user=user)


@app.route("/museot")
def museums():
    museums = get_museums()
    avg_stars = get_average_stars_for_all_museums()
    museum_list = []
    for museum in museums:
        museum_list.append({
            "id": museum.id,
            "name": museum.name,
            "bio": museum.bio,
            "img_url": museum.img_url,
            "museum_type": museum.museum_type,
            "avg_stars": int(avg_stars.get(museum.id, 0))
        })

    sort_by = request.args.get("sort", "name")
    if sort_by == "stars":
        museum_list = sorted(museum_list, key=lambda x: x["avg_stars"], reverse=True)
    else:
        museum_list = sorted(museum_list, key=lambda x: x["name"].lower())

    return render_template("museums.html", museums=museum_list, sort_by=sort_by)


@app.route("/arvostelut")
def reviews():
    museums = {museum.id: museum.name for museum in get_museums()}
    reviews = get_all_reviews()
    museums_and_reviews = [{
        "title": review.title,
        "text": review.review_text,
        "stars": review.stars,
        "username": review.username,
        "date": review.date,
        "museum_name": museums.get(review.museum_id, ""),
        "museum_id": review.museum_id}
        for review in reviews]
    
    sort_by = request.args.get("sort", "date")
    if sort_by == "stars":
        museums_and_reviews = sorted(museums_and_reviews, key=lambda x: x["stars"], reverse=True)
    elif sort_by == "title":
        museums_and_reviews = sorted(museums_and_reviews, key=lambda x: x["title"].lower())

    return render_template("reviews.html", reviews=museums_and_reviews, sort_by=sort_by)


@app.route("/poista-arvio/<int:review_id>", methods=["GET", "POST"])
def delete_review(review_id):
    museum_id = del_review(review_id)
    return redirect(url_for("show_museum", museum_id=museum_id))


@app.route("/haku", methods=["GET", "POST"])
def search():
    content = [" "]
    if request.method == "POST":
        search_word = request.form["search_field"].strip()
        search_type = request.form.get("museum_type")
        content = search_museums(search_word, search_type)
        return render_template("search.html", content=content)
    
    return render_template("search.html", content=content)


@app.route("/paikkatiedot")
def get_locations():
    locations = jsonify(get_map_details())

    return locations


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
