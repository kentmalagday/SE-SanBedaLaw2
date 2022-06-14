from flask import Flask, redirect, render_template, request, url_for, session, Blueprint
from firebase_config import *
from admin import admin

app = Flask(__name__)
app.register_blueprint(admin, url_prefix='/admin')

#routes to user/client side
@app.route('/')
@app.route('/index')
def indexPage():
    return render_template('/user-page/user_index.html')

@app.route('/search/searchValue=<searchValue>', methods=["POST", "GET"])
def searchArticle(searchValue=None):
    if request.method == "POST":
        title_checked = False
        author_checked = False
        institution_checked = False
        searchValue = request.form['searchValue']
        type = request.form.getlist['type']
        if ('title' not in type) and ('author' not in type) and ('institution' not in type):
            title_checked = True
            author_checked = True
            institution_checked = True
        if 'title' in type:
            title_checked = True
        if 'author' in type:
            author_checked = True
        if 'institution' in type:
            institution_checked = True
        #[title, author, insti]
        return render_template('/user-page/search_result.html', searchValue)

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
            #create user through Authentication in Firebase
            new_user = auth.create_user_with_email_and_password(email, password)       
            data = {"fullName" : fullName,
                    "institution" : institution,
                    "email" : email,
                    "admin" : False}
            db.child('users').child(new_user['localId']).set(data)                                     #add formatted data to Realtime DB
        except:
            existing_account = "Email in use"                                           #catch error if email is used already
            print(existing_account)
            return render_template('/user-page/user_signup.html')
        return redirect(url_for("signInPage"))
    else:
        return render_template('/user-page/user_signup.html')

@app.route('/signin', methods=["POST", "GET"])
def signInPage():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        try:
            login = auth.sign_in_with_email_and_password(email, password)
            user = db.child('users').child(login['localId']).child('admin').get()
        except:
            invalid_cred = "Invalid credentials"
            print(invalid_cred)
            return render_template('/user-page/user_signin.html')
        else:
            if user.val() is True:
                invalid_cred = "Invalid credentials"
                return render_template('/user-page/user_signin.html')
            return redirect(url_for('indexPage'))
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