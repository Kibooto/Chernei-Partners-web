from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
#from flask_login import UserMixin, LoginManager, login_user, login_required, logout_user, current_user
#from flask_wtf import wtforms
#from wtforms import StringField, PasswordField, SubmitField, EmailField
#from wtforms.validators import InputRequired, Length, Email, EqualTo, ValidationError

app = Flask(__name__)

# Config
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'secret'

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    useremail = db.Column(db.String(20), nullable=False)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(20), nullable=False)


@app.route('/', methods=['GET', 'POST'])
def index():
    current_page = '/'
    return render_template('index.html', current_page=current_page)

@app.route('/login', methods=['GET', 'POST'])
def login():
    current_page = '/login'
    return render_template('auth/login.html', current_page=current_page)

@app.route('/register', methods=['GET', 'POST'])
def register():
    current_page = '/register'
    return render_template('auth/register.html', current_page=current_page)

if __name__ == '__main__':
    app.run(debug=True)
