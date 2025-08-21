import math, secrets, sqlite3, db, config, forum, users, markupsafe,base64
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
        return redirect("/front_page/"+str(session['username']))      
    

def return_check(item_id):
    print("app.py's return_check called for item_id",item_id)
    if forum.is_borrowed(item_id) == None:
        flash("Tavara on jo varastossa")
        print("app.py's return_check flash recorded, redirecting to frontpage")
        return redirect("/front_page/"+str(session['username']))      
    
def check_owner_id(item_id):
    print("app.py's check_owner_id called for item_id",item_id)
    owner_id = int(forum.item_owner_id(item_id))
    if owner_id != int(session["user_id"]):
        print("app.py's check_owner_id owner_id != session['user_id'] visited, with owner_id =",owner_id,"session['user_id]=",session['user_id'])
        flash("Sinulla ei ole oikeutta muokata kyseistä tavaraa!")
        return redirect("/front_page/"+str(session['username']))

def check_borrower_id(item_id):
    print("app.py's check_borrower_id called for item_id",item_id)
    borrower_id = int(forum.borrower_id(item_id))
    if borrower_id != int(session["user_id"]):
        print("app.py's check_borrower_id borrower_id != session['user_id'] visited, with borrower_id =",borrower_id,"session['user_id]=",session['user_id'])        
        flash("Tavara ei ole hallussasi!")
        return redirect("/front_page/"+str(session['username']))

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

def picture_request(fieldname = "item_picture"): #do we need try except here later?
    print("app.py's picture_request called")
    file = request.files[fieldname]
    print("app.py's picture_request file.filename =",file.filename)
    if not file or file.filename == "": return None
    out = picture_check(file)
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
