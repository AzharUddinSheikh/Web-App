from flask import Flask, render_template

app = Flask(__name__)


@app.route('/')
def home():
    return render_template('indexblog.html')


@app.route('/about')
def about():
    return render_template('aboutblog.html')


@app.route('/contact')
def contact():
    return render_template('contactblog.html')


@app.route('/post')
def post():
    return render_template('postblog.html')


if __name__ == ("__main__"):
    app.run(debug=True)
