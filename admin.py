from flask import Blueprint, redirect, render_template, url_for, request, session
from firebase_config import *

admin = Blueprint('admin', __name__)

@admin.route('/')
@admin.route('/index')
def indexPage():
    admin = session.get('adminData')
    if admin is not None:
        return render_template('/admin-page/admin_index.html')
    else:
        return redirect(url_for("admin.signInAdmin"))

@admin.route('/searchValue', methods=['POST','GET'])
def searchVal():
    adminData = session.get('adminData')
    if adminData is not None:
        if request.method == 'POST':
            repoList = session.get('repoList')
            if repoList is not None:
                session['repoList'] = None
            searchVal = request.form['search']
            print(searchVal)
            repo = db.child('articles').get()
            listOfRepo = []
            for x in repo.each():
                for values in x.val().values():
                    if searchVal in values.lower():
                        listOfRepo.append((x.key(), x.val()))

            listOfRepo = [i for n, i in enumerate(listOfRepo) if i not in listOfRepo[n + 1:]]
            session['repoList'] = listOfRepo
            return redirect(url_for("admin.viewRepositoryPage"))
    else:
        return redirect(url_for('admin.signInAdmin'))
        

@admin.route("/signin", methods=["POST", "GET"])
def signInAdmin():
    adminData = session.get('adminData')
    if adminData is None:
        if request.method == "POST":
            try:
                email = request.form["email"]
                password = request.form["password"]
                adminUser = auth.sign_in_with_email_and_password(email, password)
                adminUserDb = db.child('admin').child(adminUser['localId']).get()
                userDb = db.child('users').child(adminUser['localId']).get()
                if (adminUserDb.val() is None) and (userDb.val() is None):
                    auth.delete_user_account(adminUser['idToken'])
                    session['alert'] = "Invalid credentials"
                    return redirect(url_for("admin.signInAdmin"))
                elif adminUserDb.val() is None:
                    session['alert'] = "Invalid credentials"
                    return redirect(url_for("admin.signInAdmin"))
                elif adminUserDb.val()['enabled'] is False:
                    session['alert'] = "Account is deactivated."
                    return redirect(url_for('admin.signInAdmin'))
                else:
                    adminUserInfo = auth.get_account_info(adminUser['idToken'])
                    isVerified = adminUserInfo['users'][0]['emailVerified']
            except Exception as e:
                print(e)
                session['alert'] = "Invalid credentials"
                return redirect(url_for("admin.signInAdmin"))
            else:
                if isVerified is False:
                    session['alert'] = "Account is not yet email verified. Another email has been sent out for verification."
                    auth.send_email_verification(adminUser['idToken'])
                    return redirect(url_for("admin.signInAdmin"))
                session['adminData'] = (adminUserDb.key(), adminUserDb.val())
                return redirect(url_for("admin.indexPage"))
        else:
            try:
                alert = session['alert']
                if alert is not None:
                    session.pop('alert', None)
                    return render_template('/admin-page/admin_signin.html', alert=alert)
            except:
                return render_template('/admin-page/admin_signin.html')
    else:
        return redirect(url_for('admin.indexPage'))
        
@admin.route('/forget-password', methods=["POST", "GET"])
def forgetPasswordPage():
    adminData = session.get('adminData')
    if adminData is not None:
        return redirect(url_for('admin.indexPage'))
    if request.method == "POST":
        email = request.form['email']
        isAdmin = False
        checkIfAdmin = db.child('admin').get()
        for accounts in checkIfAdmin.val():
            if checkIfAdmin.val()[accounts]['email'] == email:
                isAdmin = True
        if isAdmin is True:
            try:
                auth.send_password_reset_email(email)
            except:
                session['alert'] = "Account with inputted email not found."
                return redirect(url_for('admin.forgetPasswordPage'))
            else:
                session['alert'] = "Password reset link has been sent to your email."
                return redirect(url_for('admin.forgetPasswordPage'))
        else:
            session['alert'] = "Account with inputted email not found."
            return redirect(url_for('admin.forgetPasswordPage'))
    else:
        alert = session.get('alert')
        if alert is not None:
            session.pop('alert', None)
            return render_template('/admin-page/admin_forgetpass.html', alert=alert)
        else:
            return render_template('/admin-page/admin_forgetpass.html')

@admin.route('/header-nav')
def headerNav():
    return render_template('/admin-page/header nav.html')

@admin.route('/left-nav')
def leftNav():
    return render_template('/admin-page/left-navigation.html')

@admin.route('/right-main')
def rightMain():
    return render_template('/admin-page/right-mainwindow.html')

@admin.route('/settings')
def settingsPage():
    adminData = session.get('adminData')
    if adminData is not None:
        alert = session.get('alert')
        if alert is not None:
            session.pop('alert', None)
            return render_template('/admin-page/admin_settings.html', adminData = adminData, alert=alert)
        else:
            return render_template('/admin-page/admin_settings.html', adminData = adminData)
    else:
        return redirect(url_for('admin.signInAdmin'))

@admin.route('/settings/edit-institution/<key>', methods=["POST", "GET"])
def settingsEditInstitution(key):
    adminData = session.get('adminData')
    if adminData is not None:
        if request.method == "POST":
            newInstitution = request.form['newInstitution']
            adminKey = request.form['adminKey']
            db.child('admin').child(adminKey).update({'institution' : newInstitution})
            adminData = db.child('admin').child(adminKey).get()
            session['adminData'] = adminData
            session['alert'] = "Updated Institution Successfully."
            return redirect(url_for('settingsPage'))
        else:
            return render_template('/admin-page/admin_editInstitution.html', adminData=adminData)
    else:
        return redirect(url_for('admin.signInAdmin'))

@admin.route('/settings/edit-name/<key>', methods=["POST", "GET"])
def settingsEditName(key):
    adminData = session.get('adminData')
    if adminData is not None:
        if request.method == "POST":
            newName = request.form['newName']
            adminKey = request.form['adminKey']
            db.child('admin').child(adminKey).update({'fullName' : newName})
            adminData = db.child('admin').child(adminKey).get()
            session['adminData'] = adminData
            session['alert'] = "Updated Name Successfully."
            return redirect(url_for('settingsPage'))
        else:
            return render_template('/admin-page/admin_editName.html', adminData=adminData)
    else:
        return redirect(url_for('admin.signInAdmin'))
    
@admin.route('/settings/delete/<key>', methods=["POST", "GET"])
def deleteAccount(key):
    adminData = session.get('adminData')
    if adminData is not None:
        if request.method == "POST":
            if adminData[0] == key:
                if adminData[1]['root'] is True:
                    session['alert'] = "Root admin can not be deleted."
                    return redirect(url_for('admin.settingsPage'))
                try:
                    db.child('admin').child(key).remove()
                except:
                    session['alert'] = "No admin account with UID exists"
                    return redirect(url_for('admin.settingsPage'))
                else:
                    session['alert'] = "Account deleted from database."
                    session.pop('adminData', None)
                    return redirect(url_for('admin.signInAdmin'))
            else:
                session['alert'] = "Deleting another user is not possible."
                return redirect(url_for('admin.settingsPage'))
    else:
        return redirect(url_for('admin.signInAdmin'))

@admin.route('/help')
def helpPage():
    adminData = session.get('adminData')
    if adminData is not None:
        return render_template('/admin-page/admin_help.html')
    else:
        return redirect(url_for('admin.signInAdmin'))

@admin.route('/view-repository')
def viewRepositoryPage():
    adminData = session.get('adminData')
    if adminData is not None:
        if session.get('repoList') == None:
            repo = db.child('articles').get()
            listOfRepo = []
            for x in repo.each():
                listOfRepo.append((x.key(), x.val()))
        else:
            print('Not null')
            listOfRepo = session['repoList']
            session['repoList'] = None
                
        alert = session.get('alert')
        if alert is not None:
            session.pop('alert', None)
            return render_template('/admin-page/1view repository.html', listOfRepo=listOfRepo, alert=alert)
        return render_template('/admin-page/1view repository.html', listOfRepo=listOfRepo)
    else:
        return redirect(url_for('admin.signInAdmin'))

@admin.route('/access-requests')
def accessRequestsPage():
    adminData = session.get('adminData')
    if adminData is not None:
        listOfAccessRequests = []
        requests = db.child('requests').get()
        requestsVal = requests.val()
        for request in requestsVal:
            listOfAccessRequests.append(requestsVal[request])
        return render_template('/admin-page/4access requests.html', listOfAccessRequests=listOfAccessRequests)
    else:
        return redirect(url_for('admin.signInAdmin'))

@admin.route('/admin-table')
def viewAdminPage():
    adminData = session.get('adminData')
    if adminData is not None:
        listOfRepo = []
        admins = db.child('admin').get()
        for admin in admins:
            listOfRepo.append((admin.key(), admin.val()))
        alert = session.get('alert')
        if alert is not None:
            session.pop('alert', None)
            return render_template('/admin-page/admin_table.html', listOfRepo = listOfRepo, alert=alert)
        else:
            return render_template('/admin-page/admin_table.html', listOfRepo = listOfRepo)
    else:
        return redirect(url_for('admin.signInAdmin'))

@admin.route('/add-admin', methods=["POST", "GET"])
def addAdminPage():
    adminData = session.get('adminData')
    if adminData is not None:
        if adminData[1]['root'] is True:
            if request.method == "POST":
                name = request.form["adminName"]
                institution = request.form["adminInstitution"]
                print(institution)
                email = request.form["email"]
                password = request.form["password"]
                cpassword = request.form["cpassword"]
                if password != cpassword:
                    session['alert'] = "Mismatching passwords"
                    return redirect(url_for('admin.addAdminPage'))
                try:
                    admin = auth.create_user_with_email_and_password(email, password)
                except:
                    getAccounts = db.child('users').get()
                    accValues = getAccounts.val()
                    for account in accValues:
                        if accValues[account]['email'] == email:
                            try:
                                userToAdmin = auth.sign_in_with_email_and_password(email, password)
                            except:
                                print("User to admin -- invalid password")
                                return redirect(url_for('admin.addAdminPage'))
                            else:
                                data = {
                                    'fullName' : name,
                                    'institution' : institution,
                                    'email' : email,
                                    'root' : False,
                                    'enabled' : True
                                }
                                db.child('admin').child(userToAdmin['localId']).set(data)
                                return redirect(url_for('admin.addAdminPage'))
                        else:
                            continue
                    session['alert'] = "Admin Account already exists."
                    return redirect(url_for('admin.addAdminPage'))
                else:
                    auth.send_email_verification(admin['idToken'])
                    data = {
                        'fullName' : name,
                        'institution' : institution,
                        'email' : email,
                        'root' : False,
                        'enabled' : True
                    }
                    db.child('users').child(admin['localId']).set(data)
                    db.child('admin').child(admin['localId']).set(data)
                    session['alert'] = "Admin account has been added."
                    return redirect(url_for('admin.addAdminPage'))
            else:
                alert = session.get('alert')
                if alert is not None:
                    session.pop('alert', None)
                    return render_template('/admin-page/add_admin.html', alert = alert)
                else:
                    return render_template('/admin-page/add_admin.html')
        else:
            session['alert'] = "Only Root Admin Account can add admin accounts."
            return redirect(url_for('admin.indexPage'))
    else:
        return redirect(url_for('admin.signInAdmin'))

@admin.route('/add-article', methods=["POST", "GET"])
def addArticlePage():
    adminData = session['adminData']
    if adminData is not None:
        if request.method == "POST":
            try:
                articleTitle = request.form['articleTitle']
                author = request.form['author']
                journalTitle = request.form['journalTitle']
                abstract = request.form['abstract']
                page = request.form['page']
                date = request.form['date']
                url = request.form['url']
                doi = request.form['doi']
                authorEmail = request.form['authorEmail']
                pubType = request.form['pubType']
                adminData = session.get('adminData')
                data = {
                    "articleTitle" : articleTitle,
                    "author" : author,
                    "authorEmail" : authorEmail,
                    "journalTitle" : journalTitle,
                    "abstract" : abstract,
                    "page" : page,
                    "date" : date,
                    "url" : url,
                    "doi" : doi,
                    "pubType" : pubType,
                    "institution" : adminData['institution']
                }
                listOfArticles = db.child("articles").get()
                for article in listOfArticles:
                    articleVal = article.val()
                    if url in articleVal['url'] or doi in articleVal['doi']:
                        print("url exists")
                        return render_template('/admin-page/addarticle.html')
                db.child("articles").push(data)
                return redirect(url_for("admin.indexPage"))
            except:
                return render_template('/admin-page/addarticle.html')
        else:
            return render_template('/admin-page/addarticle.html')
    else:
        return redirect(url_for('admin.signInAdmin'))
    
@admin.route('/edit-article/<key>', methods=["POST", "GET"])
def editArticlePage(key):
    adminData = session.get('adminData')
    if adminData is not None:
        if request.method == "POST":
            articleTitle = request.form['articleTitle']
            author = request.form['author']
            journalTitle = request.form['journalTitle']
            authorEmail = request.form['authorEmail']
            abstract = request.form['abstract']
            page = request.form['page']
            date = request.form['date']
            institution = request.form['institution']
            url = request.form['url']
            doi = request.form['doi']
            pubType = request.form['pubType']
            
            data = {
                'articleTitle' : articleTitle,
                'author' : author,
                'journalTitle' : journalTitle,
                'authorEmail' : authorEmail,
                'abstract' : abstract,
                'page' : page,
                'date' : date,
                'institution' : institution,
                'url' : url,
                'doi' : doi,
                'pubType' : pubType
            }
            
            key = request.form['key']
            try:
                db.child('articles').child(key).update(data)
            except:
                session['alert'] = "Error in updating repository"
            else:
                session['alert'] = "Repository updated successfully"
            finally:
                return redirect(url_for('admin.viewRepositoryPage'))
        else:
            article = db.child('articles').child(key).get()
            articleVal = article.val()
            return render_template('/admin-page/editarticle.html', articleVal = articleVal, key=key)
    else:
        return redirect(url_for('admin.signInAdmin'))
    


@admin.route('/admin-table/delete/<key>')
def deleteAdminAccount(key):
    adminData = session.get('adminData')
    if adminData is not None:
        adminKey = session['adminData'][0]
        isRoot = db.child('admin').child(key).get()
        if isRoot.val()['root'] is True:
            session['alert'] = "Root admin can not be deleted."
            return redirect(url_for('admin.viewAdminPage'))
        if adminKey == key:
            session['alert'] = "Can not delete own account."
            return redirect(url_for('admin.viewAdminPage'))
        db.child('admin').child(key).remove()
        session['alert'] = "Deleted admin account from database. Account will be deleted completely on next user login."
        return redirect(url_for('admin.viewAdminPage'))
    else:
        return redirect(url_for('admin.signInAdmin'))

@admin.route('/view-repository/delete/<key>')
def deleteRepository(key):
    adminData = session.get('adminData')
    if adminData is not None:
        db.child('articles').child(key).remove()
        return redirect(url_for('admin.viewRepositoryPage'))
    else:
        return redirect(url_for('admin.signInAdmin'))

@admin.route('/signout')
def signOut():
    session.pop('adminData', None)
    session['alert'] = "You have been logged out."
    return redirect(url_for("admin.signInAdmin"))