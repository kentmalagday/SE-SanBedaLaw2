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
        if searchValue == "":
            return redirect(url_for('searchArticlePage'))
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
        user = session.get('userData')
        if user is not None:
            return render_template('/user-page/user_index.html')
        else:
            return redirect(url_for('signInPage'))

@app.route("/search/<searchVal>", methods=["POST", "GET"])
def searchArticle(searchVal):
    if request.method == "POST":
        searchValue = request.form['searchValue']
        session.pop('searchVal', None)
        if searchValue == "":
            return redirect(url_for("searchArticlePage"))
        session['searchVal'] = [True, True, True]
        return redirect(url_for("searchArticle", searchVal = searchValue))
    else:
        user = session.get('userData')
        if user is not None:
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
        else:
            return redirect(url_for('signInPage'))

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
        user = session.get('userData')
        if user is not None:
            return redirect(url_for('indexPage'))
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
        user = session.get('userData')
        if user is not None:
            return redirect(url_for('indexPage'))
        else:
            return render_template('/user-page/user_signin.html')
        
@app.route('/forget-password', methods = ["POST", "GET"])
def forgetPasswordPage():
    if request.method == "POST":
        email = request.form['email']
        try:
            result = auth.send_password_reset_email(email)
            print(result)
        except Exception as e:
            print(e)
            return redirect(url_for('forgetPasswordPage'))
        return redirect(url_for('signInPage'))
    else:
        return render_template('/user-page/user_forgetpass.html')
    
    
@app.route('/signout')
def signOut():
    session.pop('userData', None)
    return redirect(url_for('signInPage'))
    
@app.route('/account/settings')
def settingsPage():
    user = session.get('userData')
    if user is not None:
        return render_template('/user-page/user_settings.html', userData = user)
    else:
        return redirect(url_for('signInPage'))

@app.route('/account/help', methods=["POST", "GET"])
def helpPage():
    if request.method == "POST":
        subject = request.form["subject"]
        message = request.form["message"]
        user = session.get('userData')
        send = Mail(user, None, message, subject)
        result = send.sendMail()
        return redirect(url_for('helpPage'))
    else:
        user = session.get('userData')
        if user is not None:
            return render_template('/user-page/user_help.html', name=session['userData']['fullName'], email=session['userData']['email'])
        else:
            return redirect(url_for('signInPage'))



@app.route('/article/<key>', methods=["POST", "GET"])
def articlePage(key):
    user = session.get('userData')
    if user is not None:
        article = db.child("articles").child(key).get()
        #print(article.key())
        return render_template('/user-page/user_fullview.html', article = article.val(), key = key)
    else:
        return redirect(url_for('signInPage'))

#send email to user
@app.route('/article/<key>/request-access', methods=["POST", "GET"])
def requestAccess(key):
    user = session.get('userData')
    if user is not None:
        articleData = db.child("articles").child(key).get()
        try:
            userData = session.get('userData')
            sendMail = Mail(userData, articleData.val(), None, None)
            result = sendMail.sendMail()
            print(result)
        except:
            print("no user logged in")
        return redirect(url_for('indexPage'))
    else:
        return redirect(url_for('signInPage'))

@app.route('/search', methods=["POST", "GET"])
def searchArticlePage():
    if request.method == "POST":
        searchValue = request.form['searchValue']
        if searchValue == "":
            return redirect(url_for('searchArticlePage'))
        session.pop('searchVal', None)
        session['searchVal'] = [True, True, True]
        return redirect(url_for('searchArticle', searchVal = searchValue))
    else:
        user = session.get('userData')
        if user is not None:
            listOfArticles = []
            articles = db.child('articles').get()
            for article in articles.each():
                listOfArticles.append((article.val(), article.key()))
            return render_template('/user-page/search_result.html', searchResults = listOfArticles)
        else:
            return redirect(url_for('signInPage'))

@app.route('/contact-us')
def contactPage():
    user = session.get('userData')
    if user is not None:
        return render_template('/user-page/contactus.html')
    else:
        return redirect(url_for('indexPage'))

@app.route('/about-us')
def aboutUsPage():
    user = session.get('userData')
    if user is not None:
        return render_template('/user-page/aboutus.html')
    else:
        return redirect(url_for('indexPage'))


if __name__ == "__main__":
    app.run(debug=True)