from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)

app.secret_key = "secret_key"

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root: @127.0.0.1:3307/crudmethod'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class Data(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    phone = db.Column(db.String(100))

    def __init__(self, name, email, phone):
        self.name = name
        self.email = email
        self.phone = phone


@app.route('/insert', methods=['POST'])
def insert():

    if request.method == 'POST':
        vari_name = request.form['name']
        vari_email = request.form['email']
        vari_phone = request.form['phone']

        my_data = Data(vari_name, vari_email, vari_phone)
        db.session.add(my_data)
        db.session.commit()

        return redirect(url_for('index'))


@app.route('/')
def index():
    return render_template('index.html')


if __name__ == ("__main__"):
    app.run(debug=True)
