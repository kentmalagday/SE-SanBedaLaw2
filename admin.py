from flask import Blueprint, redirect, render_template, url_for, request
from firebase_config import *

admin = Blueprint('admin', __name__)

@admin.route('/')
def indexPage():
    return render_template('/admin-page/admin_index.html')

@admin.route("/signin", methods=["POST", "GET"])
def signInAdmin():
    if request.method == "POST":
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
    return render_template('/admin-page/admin_settings.html')

@admin.route('/help')
def helpPage():
    return render_template('/admin-page/admin_help.html')

@admin.route('/view-repository')
def viewRepositoryPage():
    return render_template('/admin-page/1view repository.html')

@admin.route('/access-requests')
def accessRequestsPage():
    return render_template('/admin-page/4access requests.html')

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
            pubType = request.form['pubType']
            data = {
                "articleTitle" : articleTitle,
                "author" : author,
                "journalTitle" : journalTitle,
                "abstract" : abstract,
                "page" : page,
                "date" : date,
                "url" : url,
                "doi" : doi,
                "pubType" : pubType
            }
            db.child("articles").push(data)
            return redirect(url_for("admin.indexPage"))
        except:
            return render_template('/admin-page/addarticle.html')
    else:
        return render_template('/admin-page/addarticle.html')

@admin.route('/signout')
def signOut():
    return redirect(url_for("admin.signInAdmin"))