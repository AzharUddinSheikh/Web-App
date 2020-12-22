from flask import Flask, render_template, request, redirect, url_for, flash
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

# fetching all data


@app.route('/')
def index():
    all_data = Data.query.all()

    return render_template('index.html', getall=all_data)

# employee added succesfully


@app.route('/insert', methods=['POST'])
def insert():

    if request.method == 'POST':
        vari_name = request.form['name']
        vari_email = request.form['email']
        vari_phone = request.form['phone']

        my_data = Data(vari_name, vari_email, vari_phone)
        db.session.add(my_data)
        db.session.commit()

        flash('Successfully Added Employee')

        return redirect(url_for('index'))

# route is for updating emloyee info


@app.route('/update', methods=['GET', 'POST'])
def update():

    if request.method == 'POST':
        # this is the hidden id which we have provided in modal edit
        my_data = Data.query.get(request.form.get('id'))

        my_data.name = request.form['name']
        my_data.email = request.form['email']
        my_data.phone = request.form['phone']

        db.session.commit()
        flash("Employee has been updated successfully")

        return redirect(url_for('index'))


# This route is for deleting our employee
@app.route('/delete/<id>/', methods=['GET', 'POST'])
def delete(id):
    my_data = Data.query.get(id)
    db.session.delete(my_data)
    db.session.commit()
    flash("Employee Deleted Successfully")

    return redirect(url_for('index'))


if __name__ == ("__main__"):
    app.run(debug=True)
