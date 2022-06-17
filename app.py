from flask import Flask, redirect, render_template, request, url_for, session, Blueprint
from firebase_config import *
from admin import admin
from mail import Mail

app = Flask(__name__)
app.register_blueprint(admin, url_prefix='/admin')
app.secret_key = "SE-SanBedaLaw"

#routes to user/client side
@app.route('/', methods=["POST", "GET"])
@app.route('/index', methods=["POST", "GET"])
def indexPage():
    if request.method == "POST":
        title_checked = False
        author_checked = False
        institution_checked = False
        searchValue = request.form['searchValue']
        types = request.form.getlist('type')
        if ('title' not in types) and ('author' not in types) and ('institution' not in types):
            title_checked = True
            author_checked = True
            institution_checked = True
        if 'title' in types:
            title_checked = True
        if 'author' in types:
            author_checked = True
        if 'institution' in types:
            institution_checked = True
        session['searchVal'] = [title_checked, author_checked, institution_checked]
        return redirect(url_for("searchArticle", searchVal = searchValue))
    else:
        return render_template('/user-page/user_index.html')

@app.route("/search/<searchVal>", methods=["POST", "GET"])
def searchArticle(searchVal):
    if request.method == "POST":
        searchValue = request.form['searchValue']
        session.pop('searchVal', None)
        session['searchVal'] = [True, True, True]
        return redirect(url_for("searchArticle", searchVal = searchValue))
    else:
        print(searchVal)
        searchResults = []
        searchVal = searchVal.lower()
        try:
            articles = db.child("articles").get()
            for article in articles:
                vals = article.val()
                if session.get('searchVal') is not None:
                    if(session['searchVal'][0]):
                        if(searchVal in vals["articleTitle"].lower()):
                            searchResults.append((vals, article.key()))
                    if(session['searchVal'][1]):
                        if(searchVal in vals["author"].lower()):
                            searchResults.append((vals, article.key()))
                    if(session['searchVal'][2]):
                        if(searchVal in vals["institution"].lower()):
                            searchResults.append((vals, article.key()))
            #print(searchResults)
            searchResults = [i for n, i in enumerate(searchResults) if i not in searchResults[n + 1:]]
            #print(searchResults)
            return render_template('/user-page/search_result.html', searchResults = searchResults)
        except:
            print("FAILED")
            return render_template('/user-page/user_index.html')

@app.route('/signup', methods=["POST", "GET"])
def signUpPage():
    if request.method == "POST":
        fullName = request.form["fullName"]
        institution = request.form["institution"]
        email = request.form["email"]
        password = request.form["password"]
        cpassword = request.form["cpassword"]
        emailSuffix = email[-7:]
        if emailSuffix != ".edu.ph":
            print("email must be school email")
            return render_template('/user-page/user_signup.html')
        if password != cpassword:       #password must match
            print("password mismatch")
            return render_template('/user-page/user_signup.html')
        elif len(password) < 8:         #password must be greater than 8
            print("password not beyond 8")
            return render_template('/user-page/user_signup.html')
        try:
            #create user through Authentication in Firebase
            new_user = auth.create_user_with_email_and_password(email, password)
            auth.send_email_verification(new_user['idToken'])
            data = {"fullName" : fullName,
                    "institution" : institution,
                    "email" : email
                    }
            db.child('users').child(new_user['localId']).set(data)                                     #add formatted data to Realtime DB
        except:
            getAccounts = db.child('admin').get()
            accValues = getAccounts.val()
            for account in accValues:
                if accValues[account]['email'] == email:
                    try:
                        adminToUser = auth.sign_in_with_email_and_password(email, password)
                        data = {
                            'fullName' : fullName,
                            'institution' : institution,
                            'email' : email
                        }
                        db.child('users').child(adminToUser['localId']).set(data)
                    except:
                        print("error")
                    return redirect(url_for("signInPage"))
            existing_account = "Error in sign-up"                                           #catch error if email is used already
            print(existing_account)
            return render_template('/user-page/user_signup.html')
        else:
            return redirect(url_for("signInPage"))
    else:
        return render_template('/user-page/user_signup.html')

@app.route('/signin', methods=["POST", "GET"])
def signInPage():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        
        try:
            user = auth.sign_in_with_email_and_password(email, password)
            email = auth.get_account_info(user['idToken'])
            isVerified = email['users'][0]['emailVerified']
            userData = db.child('users').child(user['localId']).get()
            session['userData'] = userData.val()
        except:
            invalid_cred = "Invalid credentials"
            print(invalid_cred)
            return render_template('/user-page/user_signin.html')
        else:
            if userData.val() is None:
                invalid_cred = "Invalid credentials"
                print(invalid_cred)
                return render_template('/user-page/user_signin.html')
            if isVerified is False:
                invalid_cred = "Email not verified"
                print(invalid_cred)
                return render_template('/user-page/user_signin.html')
        return redirect(url_for('indexPage'))
    else:
        return render_template('/user-page/user_signin.html')
    
@app.route('/signout')
def signOut():
    session.pop('userData', None)
    return redirect(url_for('signInPage'))
    
@app.route('/account/settings')
def settingsPage():
    return render_template('/user-page/user_settings.html')

@app.route('/account/help')
def helpPage():
    return render_template('/user-page/user_help.html', name=session['userData']['fullName'], email=session['userData']['email'])

@app.route('/article/<key>' ,  methods=["POST", "GET"])
def articlePage(key):
    article = db.child("articles").child(key).get()
    #print(article.key())
    return render_template('/user-page/user_fullview.html', article = article.val(), key = key)

#send email to user
@app.route('/article/<key>/request-access', methods=["POST", "GET"])
def requestAccess(key):
    articleData = db.child("articles").child(key).get()
    try:
        userData = session.get('userData')
        sendMail = Mail(userData, articleData.val())
        result = sendMail.sendMail()
        print(result)
    except:
        print("no user logged in")
    return redirect(url_for('indexPage'))

@app.route('/search')
def searchArticlePage():
    return render_template('/user-page/search_result.html')

@app.route('/contact-us')
def contactPage():
    return render_template('/user-page/contactus.html')

@app.route('/about-us')
def aboutUsPage():
    return render_template('/user-page/aboutus.html')


if __name__ == "__main__":
    app.run(debug=True)