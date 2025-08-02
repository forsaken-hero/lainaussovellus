import math, secrets, sqlite3, db, config, func, markupsafe
from flask import Flask, abort, flash, make_response, redirect, render_template, request, session
from werkzeug.exceptions import Forbidden

app = Flask(__name__)
app.secret_key = config.secret_key

def require_login():
    print("app.py's require_login called")
    if "user_id" not in session:
        raise Forbidden("Sinulla ei ole oikeus tähän toimintaan.")

def check_csrf(): #later can be made to render a csrf failure html?
    print("app.py's check_csrf called")
    print("printing request.form['csrf_token'], result is", request.form["csrf_token"])
    
    if request.form["csrf_token"] != session["csrf_token"]:
        abort(403)


@app.route("/", methods=["GET", "POST"])
def login():
    try:
        print("app.py's login try")  
        require_login()
        print("app.py's login, already logged in redirecting to the front_page/"+session['username'])
        return redirect("/front_page/"+str(session['username']))
    except:
        if request.method == "GET":
            print("app.py's login method get requested. session =",session.values)
            return render_template("login.html")#, next_page=request.referrer)
        if request.method == "POST":

            username = request.form["username"]
            password = request.form["password"]
            user_id = func.check_login(username, password)
            print("app.py's login method post requested. Username =", username, 'password = ',password,'user_id = ', user_id)#,'next_page = ',next_page)
            
            if user_id:
                session["user_id"] = user_id
                session["username"] = username
                session["csrf_token"] = secrets.token_hex(16)
                print('check login correct. session["user_id"] =', session["user_id"],'session["username"]=',session["username"],'session["csrf_token"] =', secrets.token_hex(16),' redirect to /front_page/',str(session["username"]))
                return redirect("/front_page/"+str(session['username']))
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
        print("app.py's register, redirecting to the front_page/"+session['username'])
        return redirect("/front_page/" + str(session['username']))
    except:
        if request.method == "GET":
            print("app.py's register method get requested.")
            return render_template("register.html", filled={},)# show_flashes = False)

        if request.method == "POST":

            username = request.form["username"]
            if not username or len(username) > 16:
                print('ABORT since not username or len(username) > 16')
                abort(403)
            password1 = request.form["password1"]
            password2 = request.form["password2"]
            print('register method post requested. username = ',username, 'password1 = ',password1,'password2 = ',password2)

            if password1 != password2:
                flash("VIRHE: Antamasi salasanat eivät ole samat")
                filled = {"username": username}
                print('not same password flash recorded. filled = ', filled)
                return render_template("register.html", filled=filled,)# show_flashes = True)

            try:
                func.create_user(username, password1)
                flash("Tunnuksen luominen onnistui, voit nyt kirjautua sisään")
                print('tunnuksen onnistuminen flash recorded. redirect to /')
                return redirect("/")
            except sqlite3.IntegrityError:
                flash("VIRHE: Valitsemasi tunnus on jo varattu")
                filled = {"username": username}
                print('tunnus on jo varattu flash recorded. filled = ',filled)
                return render_template("register.html", filled=filled,)# show_flashes = True)


@app.route("/front_page/<username>", methods=["GET","POST"])
def front_page(username):
    try:
        print("app.py's front_page try")        
        require_login()
    except:
        print("app.py's front_page, not logged in yet")
        return render_template("not_logged_in.html")
    if request.method == "GET":
        if username != session['username']: 
            print("redirecting to the right URL of /front_page/" + str(session['username']))
            return redirect("/front_page/" + str(session['username']))
        print("app.py's front_page method get. Session's user id =",session["user_id"],",session's csrf token =",session["csrf_token"],"username from URL",username)
        return render_template("front_page.html",username=session["username"],items=func.available_items())

@app.route("/upload", methods=["GET","POST"])#upload.html sends item_name & csrf_token
def upload():
    try:
        print("app.py's upload try")
        require_login()
    except:
        print("app.py's front_page except")
        return render_template("not_logged_in.html")
    
    if request.method == "GET":
        print("app.py's upload method get requested")
        classification_keys = func.classification_keys()
        return render_template("upload.html", classification_keys = classification_keys)# show_flashes = False)
    
    if request.method == "POST":  
        print("app.py's upload method post requested.")  
        check_csrf()

        item_name = request.form["item_name"]
        print("app.py's upload item_name transfer successful, with item_name = ", item_name)
        if not item_name or len(item_name) > 100:
            print("aborting from app.py's upload")
            abort(403) #check here later as it will jump to the except not logged in yet?

        item_id = func.upload_item(item_name, session["user_id"])
        print("app.py's func.upload_item succeeded")

        classification_keys_id_list = request.form.getlist("classification_checkbox[]")
        print("app.py's upload classifcation_list transfer successful, with classification_keys_id_list = ", classification_keys_id_list)
        classifications_ids = func.upload_classifications(item_id,classification_keys_id_list)

        flash("Tavaran lisäys onnistui")
        print("app.py's upload_classifications succeeded, flash recorded. classifications_ids=",classifications_ids)
        return redirect("/front_page/" + str(session['username']))

@app.route("/edit/<item_id>", methods=["GET","POST"]) #check:  when editing if the user isnt the same at this time it still works!
def edit(item_id):
    try:
        print("app.py's edit try")
        require_login()
    except:
        print("app.py's edit except")
        return render_template("not_logged_in.html")
    
    if request.method == "GET":
        print("app.py's edit method get requested")
        classification_keys = func.classification_keys()
        item_data = func.item_data(item_id)
        item_classifications = func.item_classifications(item_id)
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
        print("app.py's edit method get data retrieve succeeded, classification_keys=",classification_keys,"item_data=",item_data,"item_classifications=",item_classifications,". Now rendering upload.html")
        return render_template("upload.html", classification_keys = classification_keys, item_data = item_data, item_classifications = item_classifications)# show_flashes = False)

    if request.method == "POST":
        print("app.py's edit method post requested.")  
        check_csrf()        

        func.delete_classifications(item_id)
        
        item_name = request.form["item_name"]
        print("app.py's edit item_name transfer successful, with item_name = ", item_name)
        if not item_name or len(item_name) > 100:
            print("aborting from app.py's upload")
            abort(403) #check here later as it will jump to the except not logged in yet?  

        func.edit_item(item_id, item_name, session['user_id'])    

        classification_keys_id_list = request.form.getlist("classification_checkbox[]")
        print("app.py's edit classifcation_list transfer successful, with classification_keys_id_list = ", classification_keys_id_list)
        classifications_ids = func.upload_classifications(item_id,classification_keys_id_list)

        flash("Tavaran muokkaus onnistui")
        print("app.py's upload_classifications succeeded, flash recorded. classifications_ids=",classifications_ids)
        return redirect("/front_page/" + str(session['username']))  


@app.route("/dev")
def dev():
    print('/dev visited')
    print('item_data func returns:',forum.item_data(15))

@app.route("/logout")
def logout():
    session.clear()
    print("app.py's logout called, session cleared. session now =", session)
    return redirect("/")



@app.teardown_appcontext #Flask automatically calls the @app.teardown_appcontext function after each request — whether it succeeded or failed.
def teardown_db(exception):
    db.close_connection()





if __name__ == '__main__':
    app.run(debug=True)
