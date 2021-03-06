from flask import Flask, flash, redirect, render_template, request, url_for, session, Blueprint
from firebase_config import *
from admin import admin
from mail import Mail
from datetime import date
import datetime

app = Flask(__name__)
app.register_blueprint(admin, url_prefix='/admin')
app.secret_key = "SE-SanBedaLaw"

#routes to user/client side
@app.route('/', methods=["POST", "GET"])
@app.route('/index', methods=["POST", "GET"])
def indexPage(): #Used for searchResults either nasa Index page or when searching another value sa searchResults page
    if request.method == "POST":
        title_checked = False
        author_checked = False
        institution_checked = False
        searchValue = request.form['searchValue']
        if searchValue == "": # if empty string, reveal all articles
            searchValue = " "
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
        filters = request.form.getlist('filter') #Check if may exisiting filters
        if(filters):
            filter_dict = {"dissertation": False,
                            "journal": False,
                            "book": False,
                            "proceedings": False,
                            "readings": False,
                            "researchproject": False,
                            "startYear": '1700',
                            "endYear": '2022'}
            for filter in filters:
                filter_dict[filter] = True
            start = request.form['startYear']
            end = request.form["endYear"]
            if start:
                filter_dict['startYear'] = start
            if end:
                filter_dict['endYear'] = end
            session['filters'] = [filter for filter in filter_dict.values()]
            print(session['filters'])
        else:
            session['filters'] = [True] * 6 #No checked filters so true lahat
        session['searchVal'] = [title_checked, author_checked, institution_checked]
        print(session['searchVal'])
        if request.form.get('titleButton') == 'title':
            print('sort title')
            session['sort'] = 'title'
        elif(request.form.get('pagesButton') == 'page'):
            print('sort page')
            session['sort'] = 'page'
        elif request.form.get('dateButton') == 'date':
            print('sort date')
            session['sort'] = 'date'
        return redirect(url_for("searchArticle", searchVal = searchValue))
    else:
        user = session.get('userData')
        if user is not None:
            return render_template('/user-page/user_index.html')
        else:
            return redirect(url_for('signInPage'))

@app.route("/search/<searchVal>")
def searchArticle(searchVal):
    user = session.get('userData')
    if user is not None:
        print(searchVal)
        searchResults = []
        searchVal = searchVal.lower()
        try:
            articles = db.child("articles").get()
            for article in articles:
                vals = article.val()
                if(searchVal == " "): #If empty search value, automatically add article to searchResults
                    searchResults.append((vals, article.key()))
                    continue
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
            searchResults = [i for n, i in enumerate(searchResults) if i not in searchResults[n + 1:]]
            searchFiltered = []
            if session.get('filters') is not None:
                if session['filters'] != [True] * 6: #if may filters na nakaset magreremove ng results sa searchResults that doesnnt match those filters
                    for result in searchResults:
                        added = False
                        if (result[0]['date'].split('/')[2] < session['filters'][6]):
                            continue
                        elif (result[0]['date'].split('/')[2] > session['filters'][7]):
                            continue
                        if(session['filters'][0]):
                            if result[0]['pubType'].lower() == "dissertation" and added is False:
                                searchFiltered.append(result)
                                added = True
                                continue
                        if(session['filters'][1]):
                            if result[0]['pubType'].lower() == "journal" and added is False:
                                searchFiltered.append(result)
                                added = True
                                continue
                        if(session['filters'][2]):
                            if result[0]['pubType'].lower() == "book" and added is False:
                                searchFiltered.append(result)
                                added = True
                                continue
                        if(session['filters'][3]):
                            if result[0]['pubType'].lower() == "proceedings" and added is False:
                                searchFiltered.append(result)
                                added = True
                                continue
                        if(session['filters'][4]):
                            if result[0]['pubType'].lower() == "readings" and added is False:
                                searchFiltered.append(result)
                                added = True
                                continue
                        if(session['filters'][5]):
                            if result[0]['pubType'].lower() == "researchproject" and added is False:
                                searchFiltered.append(result)
                                added = True
                                continue
                        
                        
                else:
                    searchFiltered = searchResults
                sort = session.get('sort')
                if sort is not None:
                    if sort == 'title':
                        searchFiltered = sorted(searchFiltered, key = lambda x:x[0]['articleTitle'])
                    elif sort == 'page':
                        searchFiltered = sorted(searchFiltered, key = lambda x:int(x[0]['page']))
                    elif sort == 'date':
                        searchFiltered = sorted(searchFiltered, key = lambda x:datetime.datetime.strptime(x[0]['date'], "%m/%d/%Y"))
            return render_template('/user-page/search_result.html', searchResults = searchFiltered, searchVal = searchVal, checked = session.get('searchVal'), filters = session.get('filters'))
        except Exception as e:
            print(e)
            return render_template('/user-page/user_index.html')
    else:
        return redirect(url_for('signInPage'))

@app.route('/signup', methods=["POST", "GET"])
def signUpPage():
    user = session.get('userData')
    if user is not None:
        return redirect(url_for('indexPage'))
    else:
        if request.method == "POST":
            fullName = request.form["fullName"]
            institution = request.form["institution"]
            email = request.form["email"]
            password = request.form["password"]
            cpassword = request.form["cpassword"]
            emailSuffix = email[-7:]
            if emailSuffix != ".edu.ph":
                msg = ("Email must be school email")
                session['alert'] = msg
                return redirect(url_for('signUpPage'))
            if password != cpassword:       #password must match
                msg = ("Password mismatch")
                session['alert'] = msg
                return redirect(url_for('signUpPage'))
            elif len(password) < 8:         #password must be greater than 8
                msg = ("Password must be longer than 8 characters")
                session['alert'] = msg
                return redirect(url_for('signUpPage'))
            try:
                #create user through Authentication in Firebase
                new_user = auth.create_user_with_email_and_password(email, password)
                auth.send_email_verification(new_user['idToken'])
                data = {"fullName" : fullName,
                        "institution" : institution,
                        "email" : email,
                        "enabled" : True
                        }
                #add formatted data to Realtime DB
                db.child('users').child(new_user['localId']).set(data)
                session['alert'] = "Account Created! Please Verify Email before Signing In."
                return redirect(url_for('signInPage'))
            except:
                #catch error if email is used already
                existing_account = "Email already been used."
                session['alert'] = existing_account                                 
                return redirect(url_for("signUpPage"))
        else:
            try:
                alert = session['alert']
                if alert is not None:
                    session.pop('alert', None)
                    return render_template('/user-page/user_signup.html', alert=alert)
            except:
                return render_template('/user-page/user_signup.html')

@app.route('/signin', methods=["POST", "GET"])
def signInPage():
    user = session.get('userData')
    if user is not None:
        return redirect(url_for('indexPage'))
    else:
        if request.method == "POST":
            email = request.form["email"]
            password = request.form["password"]
            try:
                user = auth.sign_in_with_email_and_password(email, password)
                userData = db.child('users').child(user['localId']).get()
                adminData = db.child('admin').child(user['localId']).get()
                if (userData.val() is None) and (adminData.val() is None):
                    auth.delete_user_account(user['idToken'])
                elif userData.val() is None:
                    invalid_cred = "Invalid credentials"
                    session['alert'] = invalid_cred
                    return redirect(url_for('signInPage'))
                elif userData.val()['enabled'] is False:
                    session['alert'] = "User Account is deactivated."
                    return redirect(url_for('signInPage'))
                else:
                    userInfo = auth.get_account_info(user['idToken'])
                    isVerified = userInfo['users'][0]['emailVerified']
            except:
                invalid_cred = "Invalid credentials"
                session['alert'] = invalid_cred
                return redirect(url_for('signInPage'))
            else:
                if isVerified is False:
                    invalid_cred = "User Account is still not email verified. Please check your email."
                    auth.send_email_verification(user['idToken'])
                    session['alert'] = invalid_cred
                    return redirect(url_for('signInPage'))
                session['userData'] = (userData.key(), userData.val())
                return redirect(url_for('indexPage'))
        else:
            alert = session.get('alert')
            if alert is not None:
                session.pop('alert', None)
                return render_template('/user-page/user_signin.html', success=alert)
            else:
                return render_template('/user-page/user_signin.html')
        
@app.route('/forget-password', methods = ["POST", "GET"])
def forgetPasswordPage():
    if request.method == "POST":
        email = request.form['email']
        isUser = False
        checkIfUser = db.child('users').get()
        for accounts in checkIfUser.val():
            if checkIfUser.val()[accounts]['email'] == email:
                isUser = True
        if isUser is True:
            try:
                result = auth.send_password_reset_email(email)
                print(result)
                session['alert'] = "Password reset link has been sent to your email."
                return redirect(url_for('signInPage'))
            except Exception as e:
                session['alert'] = "User not found with that email."
                return redirect(url_for('forgetPasswordPage'))
        else:
            session['alert'] = "User not found with that email."
            return redirect(url_for('forgetPasswordPage'))
    else:
        alert = session.get('alert')
        if alert is not None:
            return render_template('/user-page/user_forgetpass.html', alert = alert)
        return render_template('/user-page/user_forgetpass.html')
    
    


@app.route('/signout')
def signOut():
    session.pop('userData', None)
    session['alert'] = "You have been logged out."
    return redirect(url_for('signInPage'))
    
@app.route('/account/settings')
def settingsPage():
    user = session.get('userData')
    alert = session.get('alert')
    if user is not None:
        if alert is not None:
            session.pop('alert', None)
            return render_template('/user-page/user_settings.html', userData = user, alert=alert)
        else:
            return render_template('/user-page/user_settings.html', userData = user)
    else:
        return redirect(url_for('signInPage'))
    
@app.route('/account/edit-institution/<key>', methods=["POST", "GET"])
def editInstitutionPage(key):
    user = session.get('userData')
    if user is not None:
        if request.method == "POST":
            userKey = request.form['userKey']
            newInstitution = request.form['newInstitution']
            try:
                db.child('users').child(userKey).update({"institution" : newInstitution})
            except Exception as e:
                print(e)
                print("User data not found")
            else:
                userData = db.child('users').child(userKey).get()
                session['userData'] = ((userData.key(), userData.val()))
            return redirect(url_for('settingsPage'))
        else:
            session['alert'] = "Edited Institution Successfully."
            return render_template('/user-page/user_editInstitution.html', userData = user)
    else:
        return redirect(url_for('signInPage'))
    
@app.route('/account/edit-name/<key>', methods=["POST", "GET"])
def editNamePage(key):
    user = session.get('userData')
    if user is not None:
        if request.method == "POST":
            userKey = request.form['userKey']
            newName = request.form['newName']
            try:
                db.child('users').child(userKey).update({"fullName" : newName})
            except Exception as e:
                print(e)
                print("User data not found")
            else:
                userData = db.child('users').child(userKey).get()
                session['userData'] = ((userData.key(), userData.val()))
                session['alert'] = "Edited Name Successfully."
            return redirect(url_for('settingsPage'))
        else:
            return render_template('/user-page/user_editName.html', userData = user)
    else:
        return redirect(url_for('signInPage'))
    
@app.route('/account/delete/<key>', methods=["POST", "GET"])
def deactivateUser(key):
    userData = session['userData']
    if userData is not None:
        if request.method == "POST":
            if userData[0] == key:
                try:
                    db.child('users').child(key).remove()
                except:
                    session['alert'] = "No user with given UID exists."
                    return redirect(url_for('settingsPage'))
                else:
                    session['alert'] = "Account deleted from database."
                    session.pop('userData', None)
                    return redirect(url_for('signInPage'))
            else:
                session['alert'] = "Deleting another user is not possible."
                return redirect(url_for('settingsPage'))
    else:
        return redirect(url_for('signInPage'))

@app.route('/account/help', methods=["POST", "GET"])
def helpPage():
    user = session.get('userData')
    if user is not None:
        if request.method == "POST":
            subject = request.form["subject"]
            message = request.form["message"]
            user = session.get('userData')[1]
            send = Mail(user, None, message, subject)
            result = send.sendMail()
            if result > 0:
                session['alert'] = "Thank you for sending your concern. We will get back to you later."
            else:
                session['alert'] = "There has been an error in sending your message. Please try again later."
            return redirect(url_for('helpPage'))
        else:
            alert = session.get('alert')
            if alert is not None:
                session.pop('alert', None)
                return render_template('/user-page/user_help.html', name=session['userData'][1]['fullName'], email=session['userData'][1]['email'], alert=alert)
            return render_template('/user-page/user_help.html', name=session['userData'][1]['fullName'], email=session['userData'][1]['email'])
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
            userData = session.get('userData')[1]
            #sendMail = Mail(userData, articleData.val(), None, None)
            #result = sendMail.sendMail()
            #print(result)
        except:
            print("no user logged in")
            return redirect(url_for('signInPage'))
        else:
            today = date.today()
            today = today.strftime("%Y-%m-%d")
            
            data = {
                'date' : today,
                'title' : articleData.val()['articleTitle'],
                'author' : articleData.val()['author'],
                'institution' : articleData.val()['institution'],
                'fullName' : userData['fullName'],
                'email' : userData['email'],
                'url' : articleData.val()['url']
            }
            db.child('requests').push(data)
            return redirect(url_for('indexPage'))
    else:
        return redirect(url_for('signInPage'))

@app.route('/search', methods=["POST", "GET"])
def searchArticlePage():
    return redirect(url_for("indexPage"))

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