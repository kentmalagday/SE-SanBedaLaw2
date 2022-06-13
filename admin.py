from flask import Blueprint, redirect, render_template, url_for, request

admin = Blueprint('admin', __name__)

@admin.route('/')
def adminIndex():
    return render_template('/admin-page/admin_index.html')

@admin.route("/signin", methods=["POST", "GET"])
def signInAdmin():
    if request.method == "POST":
        return redirect(url_for("admin.adminIndex"))
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

@admin.route('/add-article')
def addArticlePage():
    return render_template('/admin-page/addarticle.html')

@admin.route('/signout')
def signOut():
    return redirect(url_for("admin.signInAdmin"))