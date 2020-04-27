import os
import json
from sqlalchemy.sql import text
from flask import Flask, session,render_template,request
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from flask.json import jsonify
import requests
from werkzeug import check_password_hash, generate_password_hash, redirect
from help import *
app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

#Home Page
@app.route("/")
def index():
        return render_template("index.html")

#Validate users and Login
@app.route("/login",methods=['POST','GET'])
def login():
    #Recieved data from user for log in validation
    if request.method == "POST":
        uname = request.form.get("username")
        passwords = request.form.get("password")
        session["uname"]=uname
        if uname == "":
            return render_template("index.html",error="You must need to enter username and password")
        data = db.execute("SELECT * FROM users WHERE (name= :name)",{"name":uname}).fetchone()
        #Asign user id into session
        if data is not None:
            data=dict(data)
            session["id"]=data['id']
            #validation for password
        if data is not None:
            psw = db.execute("SELECT password FROM users WHERE (name=:name)",{"name":uname}).fetchone()
            psw=psw["password"]
            if check_password_hash(psw,passwords):
                return render_template("login.html",name=uname,password=passwords,id=session['id']) 
            else:
                return render_template("index.html",error="Please Enter Valid Password")
        else:
            return render_template("register.html",register="You Need to register First.")    
    else:
        return render_template("index.html",error="Enter Valid Data For Login")
#Registration for New User
@app.route("/register",methods=['POST'])
def register():
    uname = request.form.get("username")
    org_password = request.form.get("password")
    #validate password  
    try:
        validate_password(org_password)
    except ValueError as e:

        return render_template("register.html",error=str(e))
    #generate hash password
    passwords = generate_password_hash(org_password)
    #Enter new user information
    db.execute("INSERT INTO users (name,password) VALUES (:name,:password)",{"name":uname,"password":passwords})
    db.commit()
    return render_template("index.html",success="Your Record Successfully Saved.")

#Search books using any title,author or isdn number
@app.route("/search",methods=['POST','GET'])
def search():
    if request.method == "POST":
        isbn = request.form.get("isbn")
        title = request.form.get("title")
        author = request.form.get("author")
        books = db.execute("SELECT * FROM books WHERE isbn= :isbn OR title= :title OR author= :author",{"isbn":isbn,"title":title,"author":author}).fetchall()
        if books:
            data = []
            for book in books:
                data.append({
                    "isbn":book[0],
                    "title":book[1],
                    "author":book[2],
                    "year":book[3]
                })
                
            return render_template("booklist.html",book=data)
        else:
            return render_template("login.html",error="This book is not availabel.Please provide valid informtion.") 
    else:
        return render_template("index.html",error="This is Get method.Not Valid.")

#Adding Rating and Review in specify isbn number book
@app.route("/review/<string:isbn_no>",methods=['POST','GET'])
def review(isbn_no):
    if request.method == "POST":

        session["isbn_no"]=isbn_no
    
        rating = request.form.get("rating")
        description = request.form.get("description")
        id = session['id']

        #checkinng Validity for existing rating or review
        if rating == "" or description == "":
            return render_template("booklist.html",error_empty="Please Enter Valid Rating and Reviews For the Book.")
        else:
            review_check = db.execute("SELECT user_id FROM reviews WHERE user_id= :user_id AND isbn= :isbn",{"user_id":id,"isbn":isbn_no}).fetchone() 
            
            if review_check is None:
                review_insert = db.execute("INSERT INTO reviews(user_id,isbn,rating,description) VALUES (:user_id,:isbn,:rating,:description)",{"user_id":id,"isbn":isbn_no,"rating":rating,"description":description})
                db.commit()
                return render_template("booklist.html",success="Your Reviews Saved Successfully.",isbn_no=session['isbn_no'])
            else:
                return render_template("booklist.html",error="You already submit your review for this book.",isbn_no=session['isbn_no'])
    else:
        return render_template("login.html")

#API implementation in json form
@app.route("/book_review/<string:isbn_no>")
def book_review(isbn_no):
    #GET all data about book 
    if request.method == "GET":
        review = db.execute("SELECT r.isbn,title,author,year,COUNT(r.isbn) AS review_count,AVG(r.rating) AS avg_rating FROM books b JOIN reviews r ON b.isbn=r.isbn WHERE (b.isbn= :isbn) GROUP BY r.isbn,title,author,year",{"isbn":isbn_no}).fetchone()
        if review:
            return jsonify({
                "isbn":review[0],
                "title":review[1],
                "author":review[2],
                "year":review[3],
                "review_count":review[4],
                "avg_rating":review[5]
            })
        else:
            return jsonify({"Enter Valid ISBN number for book"})

@app.route("/logout", methods = ['POST', 'GET'])
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")
    
if __name__ == "__main__":
    app.run(debug=True)