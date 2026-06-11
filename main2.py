from flask import Flask, render_template, request,redirect
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
import json
from datetime import datetime
from flask import session
import os
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy

import pymysql
pymysql.install_as_MySQLdb()

with open('config.json', 'r') as c:
    params = json.load(c)["params"]

local_server = False
app = Flask(__name__)
app.secret_key = 'super-secret-key'
app.config['UPLOAD_FOLDER']=params['upload_location']


if(local_server):
    app.config['SQLALCHEMY_DATABASE_URI'] = params['local_uri']
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = params['prod_uri']
db = SQLAlchemy(app)
with app.app_context():
    db.create_all()


class Contacts(db.Model):
    Serial_number = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(80), nullable=False)
    phone_num = db.Column(db.String(12), nullable=False)
    message = db.Column(db.String(120), nullable=False)
    Date = db.Column(db.String(12), nullable=True)
    eMail = db.Column(db.String(20), nullable=False)


class Posts(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    tagline = db.Column(db.String(120), nullable=False)
    slug = db.Column(db.String(21), nullable=False)
    content = db.Column(db.String(120), nullable=False)
    image1 = db.Column(db.String(100))
    image2 = db.Column(db.String(100))
    image3 = db.Column(db.String(100))
    image4 = db.Column(db.String(100))
    image5 = db.Column(db.String(100))
    video1 = db.Column(db.String(100))
    proj1 = db.Column(db.String(100))
    layout = db.Column(db.String(20))
    date = db.Column(db.String(12), nullable=True)


@app.route("/")
def home():
    posts = Posts.query.filter_by().all()
    return render_template('index.html', params=params, posts=posts)


@app.route("/post/<string:post_slug>", methods=['GET'])
def post_route(post_slug):
    post = Posts.query.filter_by(slug=post_slug ).first()
    print(post_slug )
    print(post)
    print(post.content)
    return render_template('post.html', params=params, post=post)


@app.route("/about")
def about():
    return render_template('about.html', params=params)

@app.route("/certificates")
def certificates():
    return render_template("certificates.html", params=params)

@app.route("/dashboard", methods=['POST', 'GET'])
def dashboard():

    if "user" in session and session['user'] == params['admin_user']:
        posts = Posts.query.all()
        posts = Posts.query.all()
        return render_template("dashboard.html",
                               params=params,
                               posts=posts)

    if request.method == "POST":
        username = request.form.get("uname")
        userpass = request.form.get("upass")

        if username == params['admin_user'] and userpass == params['admin_password']:
            session['user'] = username
            posts = Posts.query.all()
            posts=Posts.query.all()
            return render_template("dashboard.html",
                                   params=params,
                                   posts=posts)

    return render_template("login.html",
                           params=params)

@app.route("/edit/<string:sno>", methods=['GET', 'POST'])
def edit(sno):
    if "user" in session and session['user'] == params['admin_user']:

        if request.method == "POST":
            box_title = request.form.get('title')
            tagline = request.form.get('tagline')
            slug = request.form.get('slug')
            content = request.form.get('content')
            date = datetime.now()

            if sno == '0':
                post = Posts(
                    title=box_title,
                    tagline=tagline,
                    slug=slug,
                    content=content,
                    date=date
                )
                db.session.add(post)
                db.session.commit()

            else:
                post = Posts.query.filter_by(sno=sno).first()

                post.title = box_title
                post.tagline = tagline
                post.slug = slug
                post.content = content
                post.date = date

                db.session.commit()
                return redirect('/edit/' + sno)

        post = Posts.query.filter_by(sno=sno).first()
        return render_template('edit.html',
                               params=params,
                               post=post)

@app.route("/delete/<string:sno>")
def delete(sno):
    if "user" in session and session['user'] == params['admin_user']:
        post = Posts.query.filter_by(sno=sno).first()

        if post:
            db.session.delete(post)
            db.session.commit()

    return redirect('/dashboard')

@app.route('/logout')
def logout():
    session.pop('user')
    return redirect('/dashboard')


@app.route("/uploader", methods = ['GET', 'POST'])
def uploader():
    if "user" in session and session['user']==params['admin_user']:
        if request.method=='POST':
            f = request.files['file1']
            f.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(f.filename) ))
            return "Uploaded successfully!"

@app.route("/contact", methods = ['GET', 'POST'])
def contact():
    if(request.method=='POST'):
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        message = request.form.get('message')
        entry = Contacts(Name=name, phone_num = phone, message = message,Date=datetime.now().strftime("%d-%m-%Y"),eMail = email )
        db.session.add(entry)
        db.session.commit()
    return render_template('contact.html', params=params)

app.run(debug=True)