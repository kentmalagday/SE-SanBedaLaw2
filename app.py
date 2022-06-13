from flask import Flask, redirect, render_template, request, url_for, session
from firebase_config import *

app = Flask(__name__)


#routes to user/client side
@app.route('/')
@app.route('/index')
def indexPage():
    return render_template('/user-page/user_index.html')

@app.route('/signup', methods=["POST", "GET"])
def signUpPage():
    if request.method == "POST":
        fullName = request.form["fullName"]
        institution = request.form["institution"]
        email = request.form["email"]
        password = request.form["password"]
        cpassword = request.form["cpassword"]
        if password != cpassword:       #password must match
            print("password mismatch")
            return render_template('/user-page/user_signup.html')
        elif len(password) < 8:         #password must be greater than 8
            print("password not beyond 8")
            return render_template('/user-page/user_signup.html')
        try:
            new_user = auth.create_user_with_email_and_password(email, password)       #create user through Authentication in Firebase
            data = {"userId" : new_user['localId'],                                      #create json format for user info
                    "fullName" : fullName,
                    "institution" : institution,
                    "email" : email}
            db.child('users').set(data)                                     #add formatted data to Realtime DB
        except:
            existing_account = "Email in use"                                           #catch error if email is used already
            print(existing_account)
            return render_template('/user-page/user_signup.html')
        return redirect(url_for("indexPage"))
    else:
        return render_template('/user-page/user_signup.html')

@app.route('/signin', methods=["POST", "GET"])
def signInPage():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        try:
            login = auth.sign_in_with_email_and_password(email, password)
            print(login['localId'])
            return redirect(url_for('indexPage'))
        except:
            invalid_cred = "Invalid credentials"
            print(invalid_cred)
            return render_template('/user-page/user_signin.html')
    else:
        return render_template('/user-page/user_signin.html')
    
@app.route('/account/settings')
def settingsPage():
    return render_template('/user-page/user_settings.html')

@app.route('/account/help')
def helpPage():
    return render_template('/user-page/user_help.html')

@app.route('/article')
def articlePage():
    return render_template('/user-page/user_fullview.html')

@app.route('/search')
def searchArticlePage():
    return render_template('/user-page/search_result.html')

@app.route('/contact-us')
def contactPage():
    return render_template('/user-page/contactus.html')

@app.route('/about-us')
def aboutUsPage():
    return render_template('/user-page/aboutus.html')


#routes to admin-side

if __name__ == "__main__":
    app.run(debug=True)