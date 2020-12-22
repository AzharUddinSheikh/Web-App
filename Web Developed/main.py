from flask import Flask, render_template, request, session, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from datetime import datetime
import json
import os
from werkzeug.utils import secure_filename

# how to let our json file readable here
local_server = True
with open('config.json', 'r') as c:
    params = json.load(c)["params"]

# initiating flask a
app = Flask(__name__)

# providing config to task to be done
app.config['UPLOAD_FOLDER'] = params['uploadlocation']

# setting mail config of gmail and initializing it
app.config.update(
    MAIL_SERVER='smtp@gmail.com',
    MAIL_PORT='465',
    MAIL_USE_SSL=True,
    MAIL_USERNAME=params['gmail_user'],
    MAIL_PASSWORD=params['gmail_password']
)
mail = Mail(app)

app.config['SECRET_KEY'] = 'secretkey'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# if we r working in local server
if local_server:
    app.config['SQLALCHEMY_DATABASE_URI'] = params['local_uri']
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = params['prod_uri']

db = SQLAlchemy(app)

# class for connected our db table name contacts


class Contacts(db.Model):

    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=False, nullable=False)
    phone_num = db.Column(db.String(12), unique=True, nullable=False)
    msg = db.Column(db.String(120), unique=True, nullable=False)
    date = db.Column(db.String(12), unique=False)
    email = db.Column(db.String(20), unique=False, nullable=False)

# class for connecting our db table name post


class Posts(db.Model):

    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    slug = db.Column(db.String(21), unique=True, nullable=False)
    content = db.Column(db.String(120), nullable=False)
    date = db.Column(db.String(12), unique=False, nullable=True)
    postedby = db.Column(db.String(20), unique=False, nullable=True)
    subheading = db.Column(db.String(20), unique=True, nullable=False)
    img_file = db.Column(db.String(20), unique=False, nullable=False)

# route for our blog home page already provided limited post here


@app.route('/')
def home():
    posts = Posts.query.filter_by().all()[0:params['no_of_post']]
    return render_template('indexblog.html', params=params, posts=posts)
# providing params = params i ll read this parameter in jinja template so that all paramter ll go in templates


@app.route('/about')
def about():
    return render_template('aboutblog.html', params=params)

# creating login session


@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    # checking if user already login
    if ('user' in session and session['user'] == params['admin_user']):
        posts = Posts.query.all()
        return render_template('dashboard.html', params=params, posts=posts)

    if request.method == 'POST':
        username = request.form.get('username')
        userpass = request.form.get('password')
        if (username == params['admin_user'] and userpass == params['admin_password']):
            # set session variable
            session['user'] = username

            # fetching our data to dashboard.html (GET METHOD USED )
            posts = Posts.query.all()

            return render_template('dashboard.html', params=params)

    return render_template('login.html', params=params)

# adding contact route and getting values from html and saving to db


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':

        '''add entry to the database'''
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        message = request.form.get('message')

        entry = Contacts(name=name, date=datetime.now(),
                         phone_num=phone, msg=message, email=email)
        db.session.add(entry)
        db.session.commit()

# method for getting mails when someone send msg to our db
        mail.send_message(subject='testing',
                          recipients=['azharsheikh760@gmail.com'],
                          body=message)

    return render_template('contactblog.html', params=params)

# Function for providing route(page) for every single post when tapping on particular post


@app.route('/post/<string:post_slug>', methods=['GET'])
def post_route(post_slug):
    post = Posts.query.filter_by(slug=post_slug).first()
    return render_template('postblog.html', params=params, post=post)


# Edit/add button route
@app.route('/edit/<string:sno>', methods=['GET', 'POST'])
def insert(sno):

    # check user is logged in ? then only we allow to edit our post
    if ('user' in session and session['user'] == params['admin_user']):
        # if action was post from webapp
        if request.method == 'POST':

            box_title = request.form.get('title')
            box_subheading = request.form.get('subheading')
            box_postedby = request.form.get('postedby')
            box_content = request.form.get('content')
            box_slug = request.form.get('slug')
            box_img = request.form.get('img')

            # all name from html post request are in variable
# adding our post when sno == 0

            if sno == '0':
                post = Posts(date=datetime.now(), title=box_title, slug=box_slug, content=box_content,
                             postedby=box_postedby, subheading=box_subheading, img_file=box_img)
                db.session.add(post)
                db.session.commit()

# editing our posts when sno != 0
            else:
                post = Posts.query.filter_by(sno=sno).first()
                post.title = box_title
                post.slug = box_slug
                post.subheading = box_subheading
                post.img_file = box_img
                post.postedby = box_postedby
                post.content = box_content
                post.date = datetime.now()
                db.session.commit()

                return redirect('/edit/'+sno)
        post = Posts.query.filter_by(sno=sno).first()
        return render_template('edit.html', params=params, post=post)


# creating a uploader
@app.route('/uploader', methods=['GET', 'POST'])
def uploader():
    # check the user is login or not also request is post or not
    if ('user' in session and session['user'] == params['admin_user']):
        if request.method == "POST":
            f = request.files['file1']
            f.save(os.path.join(
                app.config['UPLOAD_FOLDER'], secure_filename(f.filename)))
            return "uploaded successfully"


# creating logout session
@app.route('/logout')
def logout():
    session.pop('user')
    return redirect('/dashboard')


# deleting our data
@app.route('/delete/<string:sno>', methods=['GET', 'POST'])
def delete(sno):
    if ('user' in session and session['user'] == params['admin_user']):
        post = Posts.query.filter_by(sno=sno).first()
        db.session.delete(post)
        db.session.commit()

        return redirect('/dashboard')


if __name__ == ("__main__"):
    app.run(debug=True)
