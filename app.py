from flask import Flask, render_template, request, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
import string
from random import choices

#initializes flask server
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///urls.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

#setting up layout for database
class Urls(db.Model):
    id_ = db.Column("id_", db.Integer, primary_key = True)
    originalURL = db.Column("originalURL", db.String())
    shortURL = db.Column("shortURL", db.String(6))

    def __init__(self, originalURL, shortURL):
        self.originalURL = originalURL
        self.shortURL = shortURL

@app.before_first_request
def create_tables():
    db.create_all()

def shorten_url():
    characters = string.digits + string.ascii_letters

    while True:
        short_url = ''.join(choices(characters, k = 6))
        if not Urls.query.filter_by(shortURL=short_url).first():
            return short_url

#Routing
@app.route('/', methods=['POST', 'GET'])
def homepage():
    if request.method == 'POST':
        url_recieved = request.form['urlform']

        ##See if url is already in DB, if not, add a new URL
        found_url = Urls.query.filter_by(originalURL=url_recieved).first()
        if found_url:
            return redirect(url_for("displayShortUrl", url=found_url.shortURL))
        else:
            #create a short URL
            short_url = shorten_url()
            new_url = Urls(url_recieved, short_url)
            db.session.add(new_url)
            db.session.commit()
            return redirect(url_for("displayShortUrl", url=short_url))
    else:
        return render_template("home.html")

@app.route('/display/<url>')
def displayShortUrl(url):
    return render_template('shorturl.html', short_url_display=url)

@app.route('/<short_url>')
def redirection(short_url):
    long_url = Urls.query.filter_by(shortURL=short_url).first()
    if long_url:
        return redirect(long_url.originalURL)
    else:
        return f'<h1>Error: Url Does not exist</h1>'

if __name__ == '__main__':
    app.run(port=5000, debug=True)