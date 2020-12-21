from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:@127.0.0.1:3307/codingthunder'

db = SQLAlchemy(app)


class Contacts(db.Model):

    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=False, nullable=False)
    phone_num = db.Column(db.String(12), unique=True, nullable=False)
    msg = db.Column(db.String(120), unique=True, nullable=False)
    date = db.Column(db.String(12), unique=False)
    email = db.Column(db.String(20), unique=False, nullable=False)


@app.route('/')
def home():
    return render_template('indexblog.html')


@app.route('/about')
def about():
    return render_template('aboutblog.html')


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':

        '''add entry to the database'''
        name = request.form.get('name')
        email = request.form.get('email')
        phone = request.form.get('phone')
        message = request.form.get('message')

        entry = Contacts(name=name, phone_num=phone, msg=message, email=email)
        db.session.add(entry)
        db.session.commit()

    return render_template('contactblog.html')


@app.route('/post')
def post():
    return render_template('postblog.html')


if __name__ == ("__main__"):
    app.run(debug=True)
