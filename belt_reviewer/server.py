from flask import Flask, render_template, redirect, session, request, flash
from flask_bcrypt import Bcrypt   
import re
from datetime import datetime
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
from mysqlconnection import connectToMySQL
app=Flask(__name__)
bcrypt = Bcrypt(app)
app.secret_key= 'thisissecret'
mysql = connectToMySQL('belt_reviewer')

@app.route('/')
def index():
    return render_template('login.html')

## REGISTRATION ##
@app.route('/process', methods=['POST'])
def process():
    session['firstName'] = request.form['firstName']
    session['lastName'] = request.form['lastName']
    session['email'] = request.form['email']
    session['userName'] = request.form['userName']
    session['id'] = session['userName']
    goodForm = True
    if len(request.form['firstName']) < 1:
        flash("First Name Required!", "name")
        goodForm = False
    if len(request.form['lastName']) <1:
        flash("Last Name Required!", "lastName")
        goodForm = False

    if len(request.form['userName']) < 1:
        flash("Please enter a UserName", "userName")
        goodForm = False

    if len(request.form['email']) < 1:
        flash('Email Required', "email")
        goodForm = False

    elif not EMAIL_REGEX.match(request.form['email']):
        flash('invalid Email Address', "email")
        goodForm = False

    if len(request.form['password']) < 3:
        flash('Password must contain at least 4 characters', "password")
        goodForm = False

    else:
        pw_hash = bcrypt.generate_password_hash(request.form['password'])
        print(pw_hash)   
        goodForm = True
        mysql = connectToMySQL('belt_reviewer')
        query = "INSERT INTO users(firstName, lastName, userName, email, password, created_at, updated_at) VALUES(%(firstName)s, %(lastName)s, %(userName)s, %(email)s, %(password)s, NOW(), NOW());"
        data = {
            'firstName': request.form['firstName'],
            'lastName': request.form['lastName'],
            'userName': request.form['userName'],
            'email': request.form['email'],
            'password': pw_hash
        }
        users = mysql.query_db(query,data)
        print(data)
        flash('Thank you for registering!', "register")
        print(session)
    return redirect('/')


      



## LOGIN ####
@app.route('/login', methods=['POST'])
def login():
    if len(request.form['userName']) or len(request.form['login_password']) <1:
        flash("Login Failed", "fail")
    mysql = connectToMySQL("belt_reviewer")
    query = "SELECT * FROM users WHERE userName = %(userName)s;"
    data = { "userName" : request.form["userName"] }
    result = mysql.query_db(query, data)
    if result:
        user = result[0]
        if bcrypt.check_password_hash(user['password'], request.form['login_password']):
            session['id'] = user['id']
            session['firstName'] = user['firstName']
            # session['loggin_in'] = True
            print(session['id'])
            print('match')
            return redirect('/dashboard')

    if result == False: 
        print(bcrypt)   
        flash("You could not be logged in","fail")
    return redirect("/")

## DASHBOARD ##
@app.route('/dashboard')
def dashboard():
    if 'userName' not in session:
        return render_template('getthefuckoutofhere.html')
    mysql = connectToMySQL('belt_reviewer')
    query = "SELECT * from users LEFT JOIN books ON users.id = books.user_id LEFT JOIN reviews ON books.id = reviews.book_id;"
    show = mysql.query_db(query)

    mysql = connectToMySQL('belt_reviewer')
    query = "SELECT books.title FROM books"
    title = mysql.query_db(query)
    print(session['firstName'])
    return render_template("dashboard.html", show = show, title = title)        


## ADD A BOOK #####
@app.route('/add')
def add():
    return render_template('add.html')

@app.route('/add_book', methods=['POST'])
def add_book():
    mysql = connectToMySQL('belt_reviewer')
    query = "INSERT INTO books(title, author, created_at, updated_at, user_id) VALUES(%(title)s, %(author)s, NOW(), NOW(), %(user_id)s);"
    data = {
        "title": request.form['title'],
        "author": request.form['author'],
        "user_id": session['id']
    }
    books = mysql.query_db(query,data)
  
    
    mysql= connectToMySQL('belt_reviewer')
    query = "INSERT INTO reviews(review, rating, created_at, updated_at, book_id, user_id) VALUES(%(review)s, %(rating)s, NOW(), NOW(), %(book_id)s, %(user_id)s);"
    data={
        "review": request.form['review'],
        "rating": request.form['rating'],
        "book_id": books,
        "user_id": session['id']
    }
    reviews = mysql.query_db(query,data)
    
    return redirect('/dashboard') 



## BOOK PAGE AND ADD REVIEW ###
@app.route('/book_page/<id>')
def book_page(id):
    mysql = connectToMySQL('belt_reviewer')
    query = "SELECT users.firstName, books.title, books.author, reviews.review, reviews.rating, reviews.created_at, books.id FROM users LEFT JOIN books ON users.id = books.user_id LEFT JOIN reviews on books.id = reviews.book_id WHERE books.id = %(id)s;"
    data = { "id": id }
    novels = mysql.query_db(query,data)
    return render_template('book_page.html', novels = novels)    

@app.route('/add_review', methods = ['POST'])
def add_review():
    print("*" *50,request.form['id'])
    mysql = connectToMySQL('belt_reviewer')
    query = "INSERT INTO reviews(review, rating, created_at, book_id, user_id) VALUES (%(new_review)s, %(rating)s, NOW(), %(book_id)s, %(user_id)s);"
    data = {
        "new_review": request.form['new_review'],
        "rating": request.form['rating'],
        "book_id": request.form['id'],
        "user_id": session['id']
        
    }
    new = mysql.query_db(query,data)
    print("*" *50, session['id'])
    return redirect('/dashboard')


@app.route('/user_page/<id>')
def user_page(id):
    mysql = connectToMySQL('belt_reviewer')
    query = "SELECT * FROM users WHERE users.id = %(id)s;"
    data ={
        "id": id
    }
    users = mysql.query_db(query,data)
    return render_template('user_page.html', user = users)


@app.route('/delete/<id>')
def gone(id):
    mysql = connectToMySQL('belt_reviewer')
    query = "DELETE FROM reviews WHERE book_id = %(id)s;"
    data ={
        "id": id
    }
    print("*" *50, id)
    bye = mysql.query_db(query,data)
    return redirect('/dashboard')


    
    
        


        

 
if __name__ == "__main__":
    app.run(debug = True)


     SELECT People.Name,  Donations.Donation_Date, Donations.Party, People.Address FROM People LEFT JOIN Donations ON People.ID = Donations.People_ID WHERE People.ID = %(id)s;"