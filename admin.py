from flask import Blueprint, redirect, render_template, url_for, request, session
from firebase_config import *

admin = Blueprint('admin', __name__)

@admin.route('/')
@admin.route('/index')
def indexPage():
    return render_template('/admin-page/admin_index.html')

@admin.route("/signin", methods=["POST", "GET"])
def signInAdmin():
    if request.method == "POST":
        try:
            email = request.form["email"]
            password = request.form["password"]
            adminUser = auth.sign_in_with_email_and_password(email, password)
            adminUserDb = db.child('admin').child(adminUser['localId']).get()
            userDb = db.child('users').child(adminUser['localId']).get()
            if (adminUserDb.val() is None) and (userDb.val() is None):
                auth.delete_user_account(adminUser['idToken'])
                print("deleted account")
            elif adminUserDb.val() is None:
                print("Admin account not found")
                return redirect(url_for("admin.signInAdmin"))
            else:
                adminUserInfo = auth.get_account_info(adminUser['idToken'])
                isVerified = adminUserInfo['users'][0]['emailVerified']
        except:
            print("Admin account not found")
            return redirect(url_for("admin.signInAdmin"))
        else:
            if isVerified is False:
                print("email not verified")
                return redirect(url_for("admin.signInAdmin"))
            session['adminData'] = (adminUserDb.key(), adminUserDb.val())
            return redirect(url_for("admin.indexPage"))
    else:
        return render_template('/admin-page/admin_signin.html')

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
    adminData = session.get('adminData')[1]
    return render_template('/admin-page/admin_settings.html', adminData = adminData)

@admin.route('/help')
def helpPage():
    return render_template('/admin-page/admin_help.html')

@admin.route('/view-repository')
def viewRepositoryPage():
    repo = db.child('articles').get()
    listOfRepo = []
    for x in repo.each():
        listOfRepo.append((x.key(), x.val()))
    return render_template('/admin-page/1view repository.html', listOfRepo=listOfRepo)

@admin.route('/view-repository/<key>/delete', methods=["POST"])
def deleteRepository(key):
    print(key)
    return redirect(url_for('admin.indexPage'))

@admin.route('/access-requests')
def accessRequestsPage():
    listOfAccessRequests = []
    requests = db.child('requests').get()
    requestsVal = requests.val()
    for request in requestsVal:
        listOfAccessRequests.append(requestsVal[request])
    return render_template('/admin-page/4access requests.html', listOfAccessRequests=listOfAccessRequests)

@admin.route('/admin-table')
def viewAdminPage():
    listOfRepo = []
    admins = db.child('admin').get()
    for admin in admins:
        listOfRepo.append((admin.key(), admin.val()))
    return render_template('/admin-page/admin_table.html', listOfRepo = listOfRepo)

@admin.route('/add-admin', methods=["POST", "GET"])
def addAdminPage():
    if request.method == "POST":
        name = request.form["adminName"]
        institution = request.form["adminInstitution"]
        print(institution)
        email = request.form["email"]
        password = request.form["password"]
        cpassword = request.form["cpassword"]
        if password != cpassword:
            print("password not matching")
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
                            'email' : email
                        }
                        db.child('admin').child(userToAdmin['localId']).set(data)
                        return redirect(url_for('admin.addAdminPage'))
                else:
                    continue
            print("admin account already exists")
            return redirect(url_for('admin.addAdminPage'))
        else:
            auth.send_email_verification(admin['idToken'])
            data = {
                'fullName' : name,
                'institution' : institution,
                'email' : email
            }
            db.child('users').child(admin['localId']).set(data)
            db.child('admin').child(admin['localId']).set(data)
            return redirect(url_for('admin.addAdminPage'))
    else:
        # admin = session.get('adminData')
        # if admin is not None:
        return render_template('/admin-page/add_admin.html')
        # else:
        #     return redirect(url_for('admin.signInAdmin'))

@admin.route('/add-article', methods=["POST", "GET"])
def addArticlePage():
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

@admin.route('/<key>/delete')
def deleteAdminAccount(key):
    adminKey = session['adminData'][0]
    if adminKey == key:
        print("cannot delete own account")
        return redirect(url_for('admin.viewAdminPage'))
    db.child('admin').child(key).remove()
    return redirect(url_for('admin.viewAdminPage'))

@admin.route('/signout')
def signOut():
    session.pop('adminData', None)
    return redirect(url_for("admin.signInAdmin"))