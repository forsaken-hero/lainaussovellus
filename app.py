import math
import secrets
import sqlite3
import db
import config
import forum
import users
import markupsafe
import time
from flask import Flask, abort, flash, redirect, render_template, request, session, g
from werkzeug.exceptions import Forbidden
#from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = config.secret_key
app.config["USERNAME_PASSWORD_MINLENGTH"] = 3
app.config["USERNAME_PASSWORD_MAXLENGTH"] = 20
app.config["PICTURE_MAXSIZE_KB"] = 100
app.config["ITEM_TEXT_MINLENGTH"] = 1
app.config["ITEM_TEXT_MAXLENGTH"] = 80

@app.context_processor
def inject_data():
    return dict(
        USERNAME_PASSWORD_MINLENGTH=app.config["USERNAME_PASSWORD_MINLENGTH"],
        USERNAME_PASSWORD_MAXLENGTH=app.config["USERNAME_PASSWORD_MAXLENGTH"],
        PICTURE_MAXSIZE_KB=app.config["PICTURE_MAXSIZE_KB"],
        ITEM_TEXT_MINLENGTH = app.config["ITEM_TEXT_MINLENGTH"],
        ITEM_TEXT_MAXLENGTH = app.config["ITEM_TEXT_MAXLENGTH"]
    )

@app.template_filter()
def show_lines(content):
    content = str(markupsafe.escape(content))
    content = content.replace("\n", "<br />")
    return markupsafe.Markup(content)

@app.teardown_appcontext
def teardown_db(exception):
    db.close_connection()

def require_login():
    if "user_id" not in session:
        raise Forbidden("Sinulla ei ole oikeus tähän toimintaan.")

def check_csrf():
    if request.form["csrf_token"] != session["csrf_token"]:
        abort(403)

def login_check():
    try:
        require_login()
        return None
    except:
        flash("Et ole kirjautunut sisään. Kirjaudu sisään ensin")
        return redirect("/")

def borrow_check(item_id):
    if forum.is_borrowed(item_id) == 1:
        flash("Tavara on lainattu!")
        return redirect("/front_page/")      

def return_check(item_id):
    if forum.is_borrowed(item_id) is None:
        flash("Tavara on jo varastossa!")
        return redirect("/front_page/")      

def check_owner_id(item_id):
    owner_id = int(forum.item_owner_id(item_id))
    if owner_id != int(session["user_id"]):
        flash("Sinulla ei ole oikeutta muokata kyseistä tavaraa!")
        return redirect("/front_page/")

def check_borrower_id(item_id):
    borrower_id = int(forum.borrower_id(item_id))
    if borrower_id != int(session["user_id"]):
        flash("Tavara ei ole hallussasi!")
        return redirect("/front_page/")

def length_check(string, a, b):
    if len(string) < a or len(string) > b:
        raise ValueError("VIRHE: virheellinen syötteen pituus!")

def check_query(query):
    if not query:
        raise ValueError("VIRHE: hakusana ei annettu!") 

def picture_check(
    file,
    type=".jpg",
    maxsize=app.config["PICTURE_MAXSIZE_KB"] * 1024,
):
    if file:
        if not file.filename.endswith(type):
            raise ValueError("VIRHE: väärä tiedostomuoto")
        image = file.read()
        if len(image) > maxsize:
            raise ValueError("VIRHE: liian suuri kuva")
    return image

def picture_request(
    fieldname="item_picture",
    type=".jpg",
    maxsize=app.config["PICTURE_MAXSIZE_KB"] * 1024,
):
    file = request.files[fieldname]
    if not file or file.filename == "":
        return None
    out = picture_check(file, type, maxsize)
    return out

def characteristics_request(
    form_base = "characteristic_",
    maxlength = app.config["ITEM_TEXT_MAXLENGTH"],
):
    form_id = 0
    characteristics = {}
    while True:
        form_id += 1
        form_tag = form_base + str(form_id)
        try:
            characteristic_value = request.form[form_tag]
        except:
            break
        if not characteristic_value:
            continue
        length_check(characteristic_value, 0, maxlength)
        characteristics[form_id] = characteristic_value
    return characteristics

def user_picture_check():
    if users.has_no_picture(session["user_id"]):
        flash("Sinulla ei ole käyttäjäkuvaa!")
        return redirect("/user/" + str(session["username"]))
    
def item_picture_check(item_id):
    if forum.has_no_item_picture(item_id):
        flash("Ei ole tavarakuvaa!")
        return redirect("/item/" + str(item_id))        

"""-------------------------------APPLICATION-----------------------------"""
@app.route("/", methods=["GET", "POST"])
def login():
    try:
        require_login()
        return redirect("/front_page/")
    except:
        if request.method == "GET":
            if "csrf_token" not in session:
                session["csrf_token"] = secrets.token_hex(16)
            return render_template("login.html")
        if request.method == "POST":
            check_csrf()
            username = request.form["username"]
            password = request.form["password"]
            try:
                length_check(
                    username,
                    app.config["USERNAME_PASSWORD_MINLENGTH"],
                    app.config["USERNAME_PASSWORD_MAXLENGTH"],
                )
                length_check(
                    password,
                    app.config["USERNAME_PASSWORD_MINLENGTH"],
                    app.config["USERNAME_PASSWORD_MAXLENGTH"],
                )
            except:
                flash("VIRHE: Tarkista että sekä käyttäjätunnus että salasana on annettu oikein!")
                return redirect("/")
            user_id = users.check_login(username, password)
            if user_id:
                session["user_id"] = user_id
                session["username"] = username
                session["csrf_token"] = secrets.token_hex(16)
                return redirect("/front_page/")
            else:
                flash("VIRHE: Väärä tunnus tai salasana")
                return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    try:
        require_login()
        flash('Kirjaudu ulos ensin päästäksesi rekisteröimään uudella tunnuksella')
        return redirect("/front_page/")
    except:
        if request.method == "GET":
            return render_template("register.html", filled={})
        if request.method == "POST":
            check_csrf()
            username = request.form["username"]
            password1 = request.form["password1"]
            password2 = request.form["password2"]
            try:
                length_check(
                    username,
                    app.config["USERNAME_PASSWORD_MINLENGTH"],
                    app.config["USERNAME_PASSWORD_MAXLENGTH"],
                )
                length_check(
                    password1,
                    app.config["USERNAME_PASSWORD_MINLENGTH"],
                    app.config["USERNAME_PASSWORD_MAXLENGTH"],
                )
                length_check(
                    password2,
                    app.config["USERNAME_PASSWORD_MINLENGTH"],
                    app.config["USERNAME_PASSWORD_MAXLENGTH"],
                )
            except:
                filled = {"username": username}
                flash("VIRHE: Tarkista että sekä käyttäjätunnus että salasana on annettu oikein!")
                return render_template("register.html", filled=filled)
            if password1 != password2:
                flash("VIRHE: Antamasi salasanat eivät ole samat!")
                filled = {"username": username}
                return render_template("register.html", filled=filled)
            try:
                users.create_user(username, password1)
                flash("Tunnuksen luominen onnistui, voit nyt kirjautua sisään")
                return redirect("/")
            except sqlite3.IntegrityError:
                flash("VIRHE: Valitsemasi tunnus on jo varattu!")
                filled = {"username": username}
                return render_template("register.html", filled=filled)

@app.route("/front_page/", methods=["GET"])
@app.route("/front_page/<int:page>", methods=["GET"])
def front_page(page=1):
    check1 = login_check()
    if check1:
        return check1
    
    available_items_count = forum.available_items_count()
    page_size = 10
    page_count = math.ceil(available_items_count / page_size)
    page_count = max(page_count, 1)
    if page < 1:
        return redirect("/front_page/1")
    if page > page_count:
        return redirect("/front_page/" + str(page_count))
    return render_template(
        "front_page.html",
        available_items_count=available_items_count,
        username=session["username"],
        available_items=forum.available_items(page, page_size),
        page=page,
        page_count=page_count,
    )

@app.route("/borrowings/", methods=["GET"])
@app.route("/borrowings/<int:page>", methods=["GET"])
def borrowings(page = 1):
    check1 = login_check()
    if check1:
        return check1
    
    borrowed_items_count = forum.borrowed_items_count()
    page_size = 10
    page_count = math.ceil(borrowed_items_count / page_size)
    page_count = max(page_count, 1)
    if page < 1:
        return redirect("/borrowings/1")
    if page > page_count:
        return redirect("/borrowings/" + str(page_count))
    return render_template(
        "borrowings.html",
        borrowed_items=forum.borrowed_items(page, page_size),
        borrowed_items_count=borrowed_items_count,
        page=page,
        page_count=page_count,
    )

@app.route("/user/", methods=["GET"])
def user_page_reroute():
    check1 = login_check()
    if check1:
        return check1
    return redirect("/user/" + str(session["username"]))

@app.route("/user/<user>/", methods=["GET", "POST"])
@app.route("/user/<user>/<int:page>", methods=["GET", "POST"])
def user_page(user, page=1):
    check1 = login_check()
    if check1:
        return check1
    if request.method == "GET":
        try:
            data = users.user_id_picture(user)
            id = data["id"]
            user_picture = data["user_picture"]
        except:
            flash(f"Sovelluksessa ei ole käyttäjää, jolla tunnus on '{user}'!")
            return redirect("/front_page/")            
        user_uploads_count = forum.user_uploads_count(id)
        page_size = 10
        page_count = math.ceil(user_uploads_count / page_size)
        page_count = max(page_count, 1)
        if page < 1:
            return redirect("/user/" + user + "/1")
        if page > page_count:
            return redirect("/user/" + user + "/" + str(page_count))
        return render_template(
            "user.html",
            id=id,
            user=user,
            user_picture=user_picture,
            user_uploads_count=user_uploads_count,
            user_uploads=forum.user_uploads(id, page, page_size),
            page=page,
            page_count=page_count,
        )
    if request.method == "POST":
        check_csrf()
        try:
            user_picture = picture_request(fieldname = "user_picture")
        except:
            flash("Käyttäjäkuvan lataus epäonnistui. Tarkista tiedoston koko ja tyyppi.")
            return redirect("/user/" + session["username"])
        users.upload_picture(user_id=session["user_id"], user_picture=user_picture)
        flash("Käyttäjäkuvan lataus onnistui.")
        return redirect("/user/" + session["username"])

@app.route("/remove_user_picture", methods=["GET", "POST"])
def remove_user_picture():
    check1 = login_check()
    if check1:
        return check1
    check2 = user_picture_check()
    if check2:
        return check2
    if request.method == "GET":
        user_picture = users.user_picture(session["user_id"])
        return render_template(
            "confirmation.html",
            item_picture=user_picture,
            remove_user_picture=1,
            prev_url = request.referrer
        )
    if request.method == "POST":
        check_csrf()            
        choice = request.form.get("choice")
        if choice == "Kyllä":
            users.remove_picture(session["user_id"])
            flash("Käyttäjäkuvan poisto onnistui")
            return redirect("/user/" + session["username"])
        else:
            prev_url = request.form.get("prev_url", "/user/" + session["username"])
            return redirect(prev_url)

@app.route("/remove_item_picture/", methods=["GET", "POST"])
@app.route("/remove_item_picture/<int:item_id>", methods=["GET", "POST"])
def remove_item_picture(item_id):
    check1 = login_check()
    if check1:
        return check1
    check2 = check_owner_id(item_id)
    if check2:
        return check2
    check3 = item_picture_check(item_id)
    if check3:
        return check3
    if request.method == "GET":
        data = forum.item_name_picture(item_id)
        item_name = data["item_name"]
        item_picture = data["item_picture"]
        return render_template(
            "confirmation.html",
            item_id=item_id,
            item_name=item_name,
            item_picture=item_picture,
            remove_item_picture=1,
            prev_url=request.referrer,
        )
    if request.method == "POST":
        check_csrf()            
        choice = request.form.get("choice")
        if choice == "Kyllä":
            forum.remove_item_picture(item_id)
            flash("Tavarakuvan poisto onnistui")
            return redirect("/item/" + str(item_id))  
        else:
            prev_url = request.form.get("prev_url", "/item/" + str(item_id))
            return redirect(prev_url)        

@app.route("/upload", methods=["GET", "POST"])
def upload():
    check1 = login_check()
    if check1:
        return check1
    if request.method == "GET": 
        classification_keys = forum.classification_keys()
        characteristic_keys = forum.characteristic_keys()
        return render_template(
            "upload.html",
            classification_keys=classification_keys,
            characteristic_keys=characteristic_keys,
        )
    if request.method == "POST":  
        check_csrf()
        item_name = request.form["item_name"]
        item_location = request.form["item_location"]
        item_classifications = [int(x) for x in request.form.getlist("classification_checkbox[]")]
        item_comment = request.form.get("item_comment")
        try:
            item_characteristics = characteristics_request()
        except: 
            flash("VIRHE: Virheellinen ominaisuuksien syötteen pituus!")
            return render_template(
                "upload.html",
                item_name=item_name,
                item_location=item_location,
                item_classifications=item_classifications,
                classification_keys=forum.classification_keys(),
                characteristic_keys=forum.characteristic_keys(),
                item_comment=item_comment,
            )
        try:
            length_check(
                item_name,
                app.config["ITEM_TEXT_MINLENGTH"],
                app.config["ITEM_TEXT_MAXLENGTH"],
            )
            length_check(
                item_location,
                app.config["ITEM_TEXT_MINLENGTH"],
                app.config["ITEM_TEXT_MAXLENGTH"],
            )
            item_picture = picture_request("item_picture")
        except:
            flash("Tavaran lisäys epäonnistui. Tarkista kuvan koko ja tyyppi, sekä pakolliset kentät.")
            return render_template(
                "upload.html",
                item_name=item_name,
                item_location=item_location,
                item_classifications=item_classifications,
                item_characteristics=item_characteristics,
                classification_keys=forum.classification_keys(),
                characteristic_keys=forum.characteristic_keys(),
                item_comment=item_comment,
            )
        item_id = forum.upload_item(
            item_name=item_name,
            owner_id=session["user_id"],
            item_location=item_location,
            item_picture=item_picture,
            item_comment=item_comment,
            item_classifications=item_classifications,
            item_characteristics=item_characteristics,
        )
        flash("Tavaran lisäys onnistui")
        return redirect("/item/" + str(item_id))

@app.route("/edit/<int:item_id>", methods=["GET", "POST"])
def edit(item_id):
    check1 = login_check()
    if check1:
        return check1
    check2 = check_owner_id(item_id)
    if check2:
        return check2
    if request.method == "GET":
        classification_keys = forum.classification_keys()
        characteristic_keys = forum.characteristic_keys()
        data = forum.edit_page_data(item_id)
        item_name = data["item_name"]
        item_location = data["item_location"]
        item_picture = data["item_picture"]
        item_comment = data["item_comment"]
        item_classifications = forum.item_classifications(item_id)
        item_characteristics = forum.item_characteristics(item_id)
        return render_template(
            "upload.html",
            item_id=item_id,
            item_name=item_name,
            item_location=item_location,
            item_picture=item_picture,
            item_comment=item_comment,
            classification_keys=classification_keys,
            characteristic_keys=characteristic_keys,
            item_classifications=item_classifications,
            item_characteristics=item_characteristics,
        )
    if request.method == "POST":
        check_csrf()
        item_name = request.form["item_name"]; 
        item_location = request.form["item_location"]; 
        item_classifications = [int(x) for x in request.form.getlist("classification_checkbox[]")]
        item_comment = request.form.get("item_comment")
        try:
            item_characteristics = characteristics_request()
        except: 
            flash("VIRHE: Virheellinen ominaisuuksien syötteen pituus!")
            return render_template(
                "upload.html",
                item_id=item_id,
                item_name=item_name,
                item_location=item_location,
                item_classifications=item_classifications,
                classification_keys=forum.classification_keys(),
                characteristic_keys=forum.characteristic_keys(),
                item_comment=item_comment,
            )
        try:
            length_check(
                item_name,
                app.config["ITEM_TEXT_MINLENGTH"],
                app.config["ITEM_TEXT_MAXLENGTH"],
            )
            length_check(
                item_location,
                app.config["ITEM_TEXT_MINLENGTH"],
                app.config["ITEM_TEXT_MAXLENGTH"],
            )
            item_picture = picture_request("item_picture")
        except:
            flash("Tavaran muokkaus epäonnistui. Tarkista kuvan koko ja tyyppi, sekä pakolliset kentät.")
            return render_template(
                "upload.html",
                item_id=item_id,
                item_name=item_name,
                item_location=item_location,
                item_picture=forum.item_picture(item_id),
                item_classifications=item_classifications,
                item_characteristics=item_characteristics,
                classification_keys=forum.classification_keys(),
                characteristic_keys=forum.characteristic_keys(),
                item_comment=item_comment,
            )
        forum.edit_item(
            item_id=item_id,
            item_name=item_name,
            item_location=item_location,
            item_picture=item_picture,
            item_comment=item_comment,
            item_classifications=item_classifications,
            item_characteristics=item_characteristics,
        )
        flash("Tavaran muokkaus onnistui")
        return redirect("/item/" + str(item_id))  

@app.route("/remove/<int:item_id>", methods=["GET", "POST"])
def remove(item_id):
    check1 = login_check()
    if check1:
        return check1
    check2 = check_owner_id(item_id)
    if check2:
        return check2
    check3 = borrow_check(item_id)
    if check3:
        return check3
    if request.method == "GET": 
        data = forum.item_name_picture(item_id)
        item_name = data["item_name"]
        item_picture = data["item_picture"]
        return render_template(
            "confirmation.html",
            item_id=item_id,
            item_name=item_name,
            item_picture=item_picture,
            remove=1,
            prev_url=request.referrer,
        )
    if request.method == "POST":
        check_csrf()            
        choice = request.form.get("choice")
        if choice == "Kyllä":
            forum.remove_item(item_id)
            flash("Tavaran poisto onnistui")
            return redirect("/front_page/")  
        else:
            prev_url = request.form.get("prev_url", "/front_page/")
            return redirect(prev_url)
        
@app.route("/item/<int:item_id>", methods=["GET"])
def item(item_id):
    check1 = login_check()
    if check1:
        return check1
    
    classification_keys = forum.classification_keys()
    characteristic_keys = forum.characteristic_keys()
    item_classifications = forum.item_classifications(item_id)
    item_characteristics = forum.item_characteristics(item_id)
    data = forum.item_page_data(item_id)
    item_name = data["item_name"]
    owner_id = data["owner_id"]
    item_location = data["item_location"]
    item_picture = data["item_picture"]
    item_comment = data["item_comment"]
    owner_username = data["owner_username"]
    borrower_username = data["borrower_username"]
    borrow_clock = data["borrow_clock"]
    borrow_date = data["borrow_date"]
    if owner_id == int(session["user_id"]):
        allowed = 1
    else:
        allowed = None
    return render_template(
        "item.html",
        item_id=item_id,
        item_name=item_name,
        item_location=item_location,
        owner_username=owner_username,
        item_picture=item_picture,
        item_comment=item_comment,
        classification_keys=classification_keys,
        characteristic_keys=characteristic_keys,
        item_classifications=item_classifications,
        item_characteristics=item_characteristics,
        allowed=allowed,
        borrower_username=borrower_username,
        borrow_date=borrow_date,
        borrow_clock=borrow_clock
    )

@app.route("/borrow/<int:item_id>", methods=["GET", "POST"])
def borrow(item_id):
    check1 = login_check()
    if check1:
        return check1
    check2 = borrow_check(item_id)
    if check2:
        return check2
    if request.method == "GET":
        data = forum.item_name_picture(item_id)
        item_name = data["item_name"]
        item_picture = data["item_picture"]
        return render_template(
            "confirmation.html",
            item_id=item_id,
            item_name=item_name,
            item_picture=item_picture,
            prev_url=request.referrer,
        )
    if request.method == "POST":
        check_csrf()     
        choice = request.form.get("choice")
        if choice == "Kyllä":
            forum.borrow_item(item_id, session["user_id"])
            flash("Tavaran lainaus onnistui")
            return redirect("/front_page/")  
        else:
            prev_url = request.form.get("prev_url", "/front_page/")
            return redirect(prev_url)

@app.route("/return/<int:item_id>", methods=["GET", "POST"])
def ret (item_id):
    check1 = login_check()
    if check1:
        return check1
    check2 = return_check(item_id)
    if check2:
        return check2
    check3 = check_borrower_id(item_id)
    if check3:
        return check3
    if request.method == "GET":
        data = forum.item_name_picture(item_id)   
        item_name = data["item_name"]
        item_picture = data["item_picture"]
        return render_template(
            "confirmation.html",
            item_id=item_id,
            item_name=item_name,
            item_picture=item_picture,
            ret=1,
            prev_url=request.referrer,
        )
    if request.method == "POST":
        check_csrf()     
        choice = request.form.get("choice")
        if choice == "Kyllä":
            forum.return_item(item_id)
            flash("Tavaran palautus onnistui")
            return redirect("/front_page/")  
        else:
            prev_url = request.form.get("prev_url", "/front_page/")
            return redirect(prev_url)

@app.route("/user_borrowings/", methods=["GET"])
def user_borrowings_reroute():
    check1 = login_check()
    if check1:
        return check1
    return redirect("/user_borrowings/" + str(session["username"]))

@app.route("/user_borrowings/<user>", methods=["GET"])
@app.route("/user_borrowings/<user>/<int:page>", methods=["GET"])
def user_borrowings(user, page=1):
    check1 = login_check()
    if check1:
        return check1
    borrower_id = users.user_id(user)
    user_borrowings_count = forum.user_borrowings_count(borrower_id)
    page_size = 10
    page_count = math.ceil(user_borrowings_count / page_size)
    page_count = max(page_count, 1)
    if page < 1:
        return redirect("/user_borrowings/" + str(user) + "/1")
    if page > page_count:
        return redirect("/user_borrowings/" + str(user) + str(page_count))
    return render_template(
        "user_borrowings.html",
        borrower_id=borrower_id,
        user=user,
        user_borrowings=forum.user_borrowings(borrower_id, page, page_size),
        user_borrowings_count=user_borrowings_count,
        page=page,
        page_count=page_count,
    )

@app.route("/search", methods=["GET"])
def search():
    check1 = login_check()
    if check1:
        return check1
    query = request.args.get("query", "")
    try:
        check_query(query)
    except:
        flash("VIRHE: Hakusana ei annettu!")
        return render_template("search.html")  
    page = request.args.get("page", 1, type=int)
    page_size = 10
    return render_template(
        "search.html",
        results=forum.search(query, page, page_size),
        query=query,
        page=page,
        page_size=page_size,
    )

@app.route("/logout", methods=["POST"])
def logout():
    check_csrf()
    session.clear()
    flash("Olet kirjautunut ulos")
    return redirect("/")
