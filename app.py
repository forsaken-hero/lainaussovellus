import math, secrets, sqlite3, db, config, forum, users, markupsafe, base64, time
from flask import Flask, abort, flash, make_response, redirect, render_template, request, session, g
from werkzeug.exceptions import Forbidden
from datetime import datetime

app = Flask(__name__)
app.secret_key = config.secret_key

@app.before_request
def before_request():
    g.start_time = time.time()

@app.after_request
def after_request(response):
    elapsed_time = round(time.time() - g.start_time, 2)
    print("elapsed time:", elapsed_time, "s")
    return response

@app.template_filter()
def show_lines(content):
    content = str(markupsafe.escape(content))
    content = content.replace("\n", "<br />")
    return markupsafe.Markup(content)

def require_login():
    print("app.py's require_login called")
    if "user_id" not in session:
        raise Forbidden("Sinulla ei ole oikeus tähän toimintaan.")

def check_csrf():
    print("app.py's check_csrf called")
    print("printing request.form['csrf_token'], result is", request.form["csrf_token"])
    
    if request.form["csrf_token"] != session["csrf_token"]:
        print("bad csrf! aborting!")
        abort(403)

def login_check():
    try:
        print("app.py's login_check try")        
        require_login()
        return None
    except:
        print("app.py's login_check except, not logged in yet")
        flash("Et ole kirjautunut sisään. Kirjaudu sisään ensin")
        return redirect("/")

def borrow_check(item_id):
    print("app.py's borrow_check called for item_id",item_id)
    if forum.is_borrowed(item_id) == 1:
        flash("Tavara on jo lainattu")
        print("app.py's borrow_check flash recorded, redirecting to frontpage")
        return redirect("/front_page/")      
    

def return_check(item_id):
    print("app.py's return_check called for item_id",item_id)
    if forum.is_borrowed(item_id) == None:
        flash("Tavara on jo varastossa")
        print("app.py's return_check flash recorded, redirecting to frontpage")
        return redirect("/front_page/")      
    
def check_owner_id(item_id):
    print("app.py's check_owner_id called for item_id",item_id)
    owner_id = int(forum.item_owner_id(item_id))
    if owner_id != int(session["user_id"]):
        print("app.py's check_owner_id owner_id != session['user_id'] visited, with owner_id =",owner_id,"session['user_id]=",session['user_id'])
        flash("Sinulla ei ole oikeutta muokata kyseistä tavaraa!")
        return redirect("/front_page/")

def check_borrower_id(item_id):
    print("app.py's check_borrower_id called for item_id",item_id)
    borrower_id = int(forum.borrower_id(item_id))
    if borrower_id != int(session["user_id"]):
        print("app.py's check_borrower_id borrower_id != session['user_id'] visited, with borrower_id =",borrower_id,"session['user_id]=",session['user_id'])        
        flash("Tavara ei ole hallussasi!")
        return redirect("/front_page/")

def length_check(string,a,b):
    print("app.py's length_check called, checking string",string,"is it between",a,"-",b)
    if len(string) < a or len(string) > b:
        print('ABORT since length_check for',string,' not between',a,'-',b)
        abort(403)  

def check_query(query):
    print("app.py's check_query called, checking query", query)
    if not query:
        raise Exception("VIRHE: varmista hakusanaa")

def picture_check(file,type = ".jpg", size = 100 * 1024)  :
    print("app.py's picture_check called, checking file", file," if it is the type",type,"with max size",size)
    if file:
        if not file.filename.endswith(type):   raise Exception("VIRHE: väärä tiedostomuoto") ##check these raise later if it would be better to be flash, etc
        image = file.read()
        if len(image) > size:  raise Exception("VIRHE: liian suuri kuva")
    print("app.py's picture_check finished, returning .read() image file",image)
    return image

def picture_request(fieldname = "item_picture", type = ".jpg", size = 100 * 1024): #do we need try except here later?
    print("app.py's picture_request called")
    file = request.files[fieldname]
    print("app.py's picture_request file.filename =",file.filename)
    if not file or file.filename == "": return None
    out = picture_check(file, type, size)
    print("app.py's picture_request success, returning",out)
    return out

def picture_converter(data):
    if data:  return base64.b64encode(data).decode("utf-8")
    return None

def characteristics_request(): #fieldname?
    print("app.py's characteristics_request called")
    form_base = "characteristic_"
    form_id = 0
    characteristics = {}
    while True:
        form_id += 1
        form_tag = form_base + str(form_id)
        try:
            characteristic_value = request.form[form_tag]
            print("app.py's upload POST while's request form succeeded, form_tag =",form_tag," characteristic_value =",characteristic_value)
        except:
            print("app.py's upload POST while's request form failed!")
            break
        if not characteristic_value: continue
        characteristics[form_id] = characteristic_value
        print("app.py's upload characteristics updated for form_id",form_id,", characteristic_value",characteristic_value,"characteristics now",characteristics)
    return characteristics

''' approach to make global
@app.before_first_request
def load_keys():
    global classification_keys, characteristic_keys
    classification_keys = forum.classification_keys()
    characteristic_keys = forum.characteristic_keys()

def refresh_keys():
    global classification_keys, characteristic_keys
    classification_keys = forum.classification_keys()
    characteristic_keys = forum.characteristic_keys()

'''
@app.route("/", methods=["GET", "POST"])
def login():
    try:
        print("app.py's login try")  
        require_login()
        print("app.py's login, already logged in redirecting to the front_page/")
        return redirect("/front_page/")
    except:
        if request.method == "GET":
            print("app.py's login method get requested. session =",session.values)
            return render_template("login.html")#, next_page=request.referrer)
        if request.method == "POST":

            username = request.form["username"]
            password = request.form["password"]
            user_id = users.check_login(username, password)
            print("app.py's login method post requested. Username =", username, 'password = ',password,'user_id = ', user_id)#,'next_page = ',next_page)
            
            if user_id:
                session["user_id"] = user_id
                session["username"] = username
                session["csrf_token"] = secrets.token_hex(16)
                print('check login correct. session["user_id"] =', session["user_id"],'session["username"]=',session["username"],'session["csrf_token"] =', secrets.token_hex(16),' redirect to /front_page/',str(session["username"]))
                return redirect("/front_page/")
            else:
                flash("VIRHE: Väärä tunnus tai salasana")
                print('Väärä tunnus tai salasana flash recorded. Redirecting to /')
                return render_template("login.html")



@app.route("/register", methods=["GET", "POST"])
def register():
    try:
        print("app.py's register try")  
        require_login()
        flash('Kirjaudu ulos ensin päästäksesi rekisteröimään uudella tunnuksella')
        print("app.py's register, redirecting to the front_page/")
        return redirect("/front_page/")
    except:
        if request.method == "GET":
            print("app.py's register method get requested.")
            return render_template("register.html", filled={},)# show_flashes = False)

        if request.method == "POST":

            username = request.form["username"]; length_check(username,3,20)
            password1 = request.form["password1"]; length_check(password1,3,20)
            password2 = request.form["password2"]; length_check(password2,3,20)
            print("app.py's register method post requested. username = ",username, 'password1 = ',password1,'password2 = ',password2)

            if password1 != password2:
                flash("VIRHE: Antamasi salasanat eivät ole samat")
                filled = {"username": username}
                print('not same password flash recorded. filled = ', filled)
                return render_template("register.html", filled=filled,)# show_flashes = True)

            try:
                users.create_user(username, password1)
                flash("Tunnuksen luominen onnistui, voit nyt kirjautua sisään")
                print('tunnuksen onnistuminen flash recorded. redirect to /')
                return redirect("/")
            except sqlite3.IntegrityError:
                flash("VIRHE: Valitsemasi tunnus on jo varattu")
                filled = {"username": username}
                print('tunnus on jo varattu flash recorded. filled = ',filled)
                return render_template("register.html", filled=filled)# show_flashes = True)


@app.route("/front_page/", methods=["GET","POST"])
@app.route("/front_page/<int:page>", methods=["GET","POST"])
def front_page(page = 1):
    check1 = login_check()
    if check1: return check1

    if request.method == "GET":
        print("app.py's front_page method get requested, for front_page/" + str(page))

        available_items_count = forum.available_items_count()
        page_size = 10
        page_count = math.ceil(available_items_count / page_size)
        page_count = max(page_count, 1)

        if page < 1:
            return redirect("/front_page/1")
        if page > page_count:
            return redirect("/front_page/" + str(page_count))

        print("app.py's front_page method get finished, rendering front_page.html")
        return render_template("front_page.html", available_items_count = available_items_count, username = session['username'], available_items = forum.available_items(page, page_size), page = page, page_count = page_count)

@app.route("/borrowings/", methods=["GET","POST"])
@app.route("/borrowings/<int:page>", methods=["GET","POST"])
def borrowed(page = 1):
    check1 = login_check()
    if check1: return check1

    if request.method == "GET":
        print("app.py's borrowed method get requested, for borrowed/" + str(page))
        
        borrowed_items_count = forum.borrowed_items_count()
        page_size = 10
        page_count = math.ceil(borrowed_items_count / page_size)
        page_count = max(page_count, 1)


        if page < 1:
            return redirect("/borrowings/1")
        if page > page_count:
            return redirect("/borrowings/" + str(page_count))

        print("app.py's borrowed method get finished, rendering borrowed.html")
        return render_template("borrowings.html", borrowed_items = forum.borrowed_items(page, page_size), borrowed_items_count = borrowed_items_count, page = page, page_count = page_count)

@app.route("/user/", methods=["GET"])
def user_page_reroute():
    check1 = login_check()
    if check1: return check1

    if request.method == "GET":
        print("app.py's user_page_reroute method get requested")
        return redirect("/user/" + str(session["username"]))

@app.route("/user/<user>/", methods=["GET","POST"])
@app.route("/user/<user>/<int:page>", methods=["GET","POST"])
def user_page(user, page = 1):
    check1 = login_check()
    if check1: return check1

    if request.method == "GET":
        print("app.py's user_page method get requested, for user/" + user + "/" + str(page))
        try:
            print("app.py's user_page try for user", user)
            id, user_picture = users.user_id_picture(user)
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

        print("app.py's user_page method get finished, rendering user_page.html")
        return render_template("user_page.html", id = id, user = user, user_picture = user_picture, user_uploads_count = user_uploads_count, user_uploads = forum.user_uploads(id, page, page_size), page = page, page_count = page_count)

    if request.method == "POST":
        print("app.py's user_page method post requested, for user/" + user + "/" + str(page))
        check_csrf()
        
        try:
            user_picture = picture_request(fieldname = "user_picture")
        except:
            flash("Käyttäjäkuvan lataus epäonnistui. Tarkista tiedoston koko ja tyyppi.")
            print("app.py's user_page post except. Flash reorded and redirecting to /user/",session["username"])
            return redirect("/user/" + session["username"])

        print("app.py's user_page picture transfer successful, with picture ", user_picture)

        users.upload_picture(user_id = session["user_id"], user_picture = user_picture)

        flash("Käyttäjäkuvan lataus onnistui.")
        return redirect("/user/" + session["username"])


@app.route("/upload", methods=["GET","POST"])#upload.html sends item_name & csrf_token
def upload():
    check1 = login_check()
    if check1: return check1    
    if request.method == "GET": 
        print("app.py's upload method get requested")
        classification_keys = forum.classification_keys()
        characteristic_keys = forum.characteristic_keys()
        print("app.py's upload method get data transfer succeeded, rendering template upload.html")
        return render_template("upload.html", classification_keys = classification_keys, characteristic_keys = characteristic_keys)# show_flashes = False)
    
    if request.method == "POST":  
        print("app.py's upload method post requested.")  
        check_csrf()

        item_name = request.form["item_name"]; length_check(item_name,1,100)
        print("app.py's upload item_name transfer successful, with item_name = ", item_name)

        item_location = request.form["item_location"]; length_check(item_location,1,100)
        print("app.py's upload item_name transfer successful, with item_name = ", item_location)

        item_classifications = [int(x) for x in request.form.getlist('classification_checkbox[]')]
        print("app.py's upload classifcations transfer successful, with item_classifications = ", item_classifications) #data produced such as item_classifications =  ['2', '6', '8']
        item_characteristics = characteristics_request()
        print("app.py's upload characteristics_request transfer successful, with item_characteristics = ", item_characteristics)#data produced such as item_characteristics =  {2: 'ff', 5: 'efefe'}
        item_comment = request.form.get("item_comment")
        
        try:
            item_picture = picture_request("item_picture")
        except:
            flash("Kuvan lataus epäonnistui. Tarkista kuvan koko ja tyyppi.")
            return render_template("upload.html", item_name = item_name, item_location = item_location, item_classifications = item_classifications,item_characteristics = item_characteristics, classification_keys = forum.classification_keys(), characteristic_keys = forum.characteristic_keys(), item_comment = item_comment)

        print("app.py's upload picture transfer successful, with picture ", item_picture)

        forum.upload_item(item_name = item_name, owner_id = session["user_id"],item_location = item_location, item_picture = item_picture, item_comment = item_comment, item_classifications = item_classifications, item_characteristics = item_characteristics)

        flash("Tavaran lisäys onnistui")
        print("app.py's upload succeeded, flash recorded. Redirecting to front_page")
        return redirect("/front_page/")

@app.route("/edit/<item_id>", methods=["GET","POST"])
def edit(item_id):
    check1 = login_check()
    if check1: return check1
    check2 = check_owner_id(item_id)
    if check2: return check2

    if request.method == "GET":
        print("app.py's edit method get requested")
        
        classification_keys = forum.classification_keys()
        characteristic_keys = forum.characteristic_keys()
        item_name_location_picture_comment = forum.item_name_location_picture_comment(item_id)
        item_classifications = forum.item_classifications(item_id)
        item_characteristics = forum.item_characteristics(item_id)
        '''
        ###################################
        classification_keys_check = []
        for data in classification_keys:
            classification_keys_check.append(data[0])
        item_classifications_check = []
        for data in item_classifications:
            item_classifications_check.append(data)
        print('..................................................')
        print('CHECK. value of classification_keys is', classification_keys_check,'value of item_classifications is',item_classifications_check)
        print('..................................................')
        ##################################
        '''
        item_picture = picture_converter(item_name_location_picture_comment[2])
        print("app.py's edit method get data retrieve succeeded, classification_keys=",classification_keys,"item_name_location_picture_comment=",item_name_location_picture_comment,"item_classifications=",item_classifications,". Now rendering upload.html")
        return render_template("upload.html", item_id = item_id, item_name = item_name_location_picture_comment[0],item_location = item_name_location_picture_comment[1], item_picture = item_picture, item_comment = item_name_location_picture_comment[3], classification_keys = classification_keys, characteristic_keys = characteristic_keys, item_classifications = item_classifications, item_characteristics = item_characteristics)

    if request.method == "POST":
        print("app.py's edit method post requested.")  
        check_csrf()        

        item_name = request.form["item_name"]; length_check(item_name,1,100)
        print("app.py's edit item_name transfer successful, with item_name = ", item_name)
        item_location = request.form["item_location"]; length_check(item_name,1,100)
        print("app.py's edit item_location transfer successful, with item_location = ", item_location)
        item_classifications = [int(x) for x in request.form.getlist('classification_checkbox[]')]
        print("app.py's edit classifcations transfer successful, with item_classifications = ", item_classifications)

        item_characteristics = characteristics_request()
        print("app.py's edit ccharacteristics transfer successful, with characteristics = ", item_characteristics)
        item_comment = request.form.get("item_comment")
        
        try:
            item_picture = picture_request("item_picture")
        except:
            flash("Kuvan lataus epäonnistui. Tarkista kuvan koko ja tyyppi.")
            return render_template("upload.html", item_id = item_id, item_name = item_name, item_location = item_location,item_picture = picture_converter(forum.item_picture(item_id)), item_classifications = item_classifications,item_characteristics = item_characteristics, classification_keys = forum.classification_keys(), characteristic_keys = forum.characteristic_keys(), item_comment = item_comment)

        
        print("app.py's edit picture transfer successful, with picture ", item_picture)

        if item_picture == None:
            print("app.py's edit: user don't change picture, picture should still be the same")
            item_picture = forum.item_picture(item_id)


        forum.edit_item(item_id=item_id,item_name=item_name,item_location = item_location, item_picture=item_picture,item_comment=item_comment,item_classifications=item_classifications,item_characteristics=item_characteristics)

        flash("Tavaran muokkaus onnistui")
        print("app.py's edit_item succeeded, flash recorded")
        return redirect("/front_page/")  

@app.route("/remove/<item_id>", methods=["GET","POST"])
def remove(item_id):
    check1 = login_check()
    if check1: return check1
    check2 = check_owner_id(item_id)
    if check2: return check2

    if request.method == "GET": 
        print("app.py's remove method get requested")
        item_name, item_picture = forum.item_name_picture(item_id)
        picture_b64 = picture_converter(item_picture)
        print("app.py's remove method get data retrieve succeeded, item_name =",item_name,". Now rendering confirmation.html")
        return render_template("confirmation.html", item_id=item_id, item_name = item_name, item_picture = picture_b64, remove = 1)

    if request.method == "POST":
        print("app.py's remove method post requested") 
        check_csrf()            
        choice = request.form.get("choice")
        if choice == "Kyllä":
            print("app.py's remove kylla button pressed")
            forum.remove_item(item_id)
            flash("Tavaran poisto onnistui")
            print("app.py's remove_item succeeded, redirecting to front_page")
        return redirect("/front_page/")  
        
@app.route("/item/<item_id>", methods=["GET","POST"])
def item(item_id):
    check1 = login_check()
    if check1: return check1

    if request.method == "GET":
        print("app.py's item method get requested, for item_id",item_id)
        classification_keys = forum.classification_keys()
        characteristic_keys = forum.characteristic_keys()
        item_name, owner_id, item_location, item_picture, item_comment = forum.item_name_ownerid_location_picture_comment(item_id)
        item_picture = picture_converter(item_picture)
        item_classifications = forum.item_classifications(item_id)
        item_characteristics = forum.item_characteristics(item_id)
        owner_username = users.username(owner_id)
        borrower_username, borrow_clock, borrow_date = forum.borrower_username_time(item_id)

        if owner_id == int(session["user_id"]): allowed = 1
        else: allowed = None
        print("app.py's item method get data requests done, with item_name =",item_name,", owner_id =",owner_id," item_picture = ",item_picture,", item_comment = ",item_comment,",owner_username = ",owner_username,",allowed=",allowed)
        return render_template("item.html", item_id = item_id,item_name = item_name,item_location = item_location,owner_username = owner_username, item_picture = item_picture, item_comment=item_comment,classification_keys = classification_keys, characteristic_keys = characteristic_keys, item_classifications = item_classifications, item_characteristics = item_characteristics,  allowed = allowed, borrower_username = borrower_username, borrow_date = borrow_date, borrow_clock = borrow_clock)

@app.route("/borrow/<item_id>", methods=["GET","POST"])
def borrow(item_id):
    check1 = login_check()
    if check1: return check1
    check2 = borrow_check(item_id)
    if check2: return check2

    if request.method == "GET":
        print("app.py's borrow method get requested")
        item_name, item_picture = forum.item_name_picture(item_id)
        picture_b64 = picture_converter(item_picture)
        print("app.py's borrow method get data retrieve succeeded, item_name =",item_name,". Now rendering confirmation.html")
        return render_template("confirmation.html", item_id=item_id, item_name = item_name, item_picture = picture_b64)        

    if request.method == "POST":
        print("app.py's borrow method post requested") 
        check_csrf()     
        choice = request.form.get("choice")
        if choice == "Kyllä":
            print("app.py's borrow kylla button pressed")
            forum.borrow_item(item_id,session["user_id"])
            flash("Tavaran lainaus onnistui")
            print("app.py's borrow_item succeeded, redirecting to front_page")
        return redirect("/front_page/")  

@app.route("/return/<item_id>", methods=["GET","POST"])
def ret (item_id):
    check1 = login_check()
    if check1: return check1
    check2 = return_check(item_id)
    if check2: return check2
    check3 = check_borrower_id(item_id)
    if check3: return check3

    if request.method == "GET":
        print("app.py's ret method get requested")
        item_name, item_picture = forum.item_name_picture(item_id)
        picture_b64 = picture_converter(item_picture)        
        print("app.py's borrow method get data retrieve succeeded, item_name =",item_name,". Now rendering confirmation.html")
        return render_template("confirmation.html", item_id=item_id, item_name = item_name, item_picture = picture_b64, ret = 1)        

    if request.method == "POST":
        print("app.py's return method post requested") 
        check_csrf()     
        choice = request.form.get("choice")
        if choice == "Kyllä":
            print("app.py's return kylla button pressed")
            forum.return_item(item_id)
            flash("Tavaran palautus onnistui")
            print("app.py's return succeeded, redirecting to front_page")
        return redirect("/front_page/")  

@app.route("/user_borrowings/", methods=["GET"])
def user_borrowings_reroute():
    check1 = login_check()
    if check1: return check1

    if request.method == "GET":
        print("app.py's user_borrowings_reroute method get requested")
        return redirect("/user_borrowings/" + str(session["username"]))

@app.route("/user_borrowings/<user>", methods=["GET","POST"])
@app.route("/user_borrowings/<user>/<int:page>", methods=["GET","POST"])
def user_borrowings(user, page = 1):
    check1 = login_check()
    if check1: return check1

    if request.method == "GET":
        print("app.py's borrowed method get requested, for user" + str(user))
        
        borrower_id = users.user_id(user)
        user_borrowings_count = forum.user_borrowings_count(borrower_id)
        page_size = 10
        page_count = math.ceil(user_borrowings_count / page_size)
        page_count = max(page_count, 1)


        if page < 1:
            return redirect("/user_borrowings/" + str(user) + "/1")
        if page > page_count:
            return redirect("/user_borrowings/" + str(user) + str(page_count))

        print("app.py's borrowed method get finished, rendering borrowed.html")
        return render_template("user_borrowings.html", borrower_id = borrower_id, user=user,user_borrowings = forum.user_borrowings(borrower_id, page, page_size), user_borrowings_count = user_borrowings_count, page = page, page_count = page_count)

@app.route("/search", methods=["GET","POST"])
def search ():
    check1 = login_check()
    if check1: return check1

    if request.method == "GET":
        print("app.py's search method get requested")

        query = request.args.get("query", "")
        
        try: check_query(query)
        except:
            flash("VIRHE: varmista hakusanaa")
            return render_template("search.html")  
        
        page = request.args.get("page", 1, type=int)

        page_size = 10

        results = forum.search(query, page, page_size)

        print("app.py's search finished, with len(results)=",len(results),". Rendering search.html")

        return render_template("search.html", results = results, query = query, page = page, page_size = page_size)
    '''
    if request.method == "POST":
        print("app.py's search method post requested")
        query = request.form.get("query")
        print("app.py's query transfer successful, with query",query)
        try: check_query(query)
        except:
            flash("VIRHE: varmista hakusanaa")
            return redirect("/search")  
        
        results = forum.search(query)
        if len(results) == 0: results = None
        username = session["username"]
        print("app.py's query done rendering search.html with results",results)
        return render_template("search.html", results = results, query = query, username = username)
    '''



@app.route("/dev")
def dev():
    print('/dev visited')
    check = forum.search("e")
    print("printing forum.search('h')",check)

    '''
    print("printing len(forum.search('h')",len(check))
    for i in range(len(check)):
        #print(f"printing forum.is_borrowed('h')[{i}]",check[i])   
        for j in range(len(check[i])):
            print(f"dev printing forum.search('h')[{i}][{j}], value is",check[i][j])
    '''


@app.route("/logout")
def logout():
    session.clear()
    flash("Olet kirjautunut ulos")
    print("app.py's logout called, session cleared. session now =", session)
    return redirect("/")



@app.teardown_appcontext #Flask automatically calls the @app.teardown_appcontext function after each request — whether it succeeded or failed.
def teardown_db(exception):
    db.close_connection()





if __name__ == '__main__':
    app.run(debug=True)
