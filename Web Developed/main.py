from flask import Flask, render_template, request, session, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from datetime import datetime
import json


# how to let our json file readable here
local_server = True
with open('config.json', 'r') as c:
    params = json.load(c)["params"]

app = Flask(__name__)

# setting mail config of gmail
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


class Contacts(db.Model):

    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=False, nullable=False)
    phone_num = db.Column(db.String(12), unique=True, nullable=False)
    msg = db.Column(db.String(120), unique=True, nullable=False)
    date = db.Column(db.String(12), unique=False)
    email = db.Column(db.String(20), unique=False, nullable=False)


class Posts(db.Model):

    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    slug = db.Column(db.String(21), unique=True, nullable=False)
    content = db.Column(db.String(120), nullable=False)
    date = db.Column(db.String(12), unique=False, nullable=True)
    postedby = db.Column(db.String(20), unique=False, nullable=True)
    subheading = db.Column(db.String(20), unique=True, nullable=False)
    img_file = db.Column(db.String(20), unique=False, nullable=False)


@app.route('/')
def home():
    posts = Posts.query.filter_by().all()[0:params['no_of_post']]
    return render_template('indexblog.html', params=params, posts=posts)
# providing params = params i ll read this parameter in jinja template so that all paramter ll go in templates


@app.route('/about')
def about():
    return render_template('aboutblog.html', params=params)


@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if ('user' in session and session['user'] == params['admin_user']):
        posts = Posts.query.all()
        return render_template('dashboard.html', params=params, posts=posts)

    if request.method == 'POST':
        username = request.form.get('username')
        userpass = request.form.get('password')
        if (username == params['admin_user'] and userpass == params['admin_password']):
            # set session variable
            session['user'] = username

            # fetching our data to dashboard.html
            posts = Posts.query.all()

            return render_template('dashboard.html', params=params)

    return render_template('login.html', params=params, posts=posts)


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

        mail.send_message(subject='testing',
                          recipients=['azharsheikh760@gmail.com'],
                          body=message)

    return render_template('contactblog.html', params=params)


@app.route('/post/<string:post_slug>', methods=['GET'])
def post_route(post_slug):
    post = Posts.query.filter_by(slug=post_slug).first()
    return render_template('postblog.html', params=params, post=post)


# Edit button route
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
            # if sno == 0 then we add new user if sno is something else then we edit

            if sno == '0':
                post = Posts(date=datetime.now(), title=box_title, slug=box_slug, content=box_content,
                             postedby=box_postedby, subheading=box_subheading, img_file=box_img)
                db.session.add(post)
                db.session.commit()

        return render_template('edit.html', params=params, sno=sno)


if __name__ == ("__main__"):
    app.run(debug=True)
