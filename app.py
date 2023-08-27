from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy
import bcrypt
import requests


open_weather_token = "bbb49be51783dd121e1aeca6a963e01f"

app = Flask(__name__)

# Config
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'secret'
app.secret_key = 'secret'

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    useremail = db.Column(db.String(20), nullable=False)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(128), nullable=False)  

    def __init__(self, useremail, username, password):
        self.useremail = useremail 
        self.username = username
        self.password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password.encode('utf-8'))


@app.route('/', methods=['GET', 'POST'])
def index():
    current_page = '/'
    return render_template('index.html', current_page=current_page)

@app.route('/register', methods=['GET', 'POST'])
def register():
    current_page = '/register'

    if not session.get('logged_in'):
        if request.method == 'POST':
            useremail = request.form['useremail']
            username = request.form['username']
            password = request.form['password']

            print(useremail, username, password)

            new_user = User(useremail=useremail, username=username, password=password)
            db.session.add(new_user)
            db.session.commit()

            return redirect('/login')

        return render_template('auth/register.html', current_page=current_page)
    else:
        return redirect('/dashboard')

@app.route('/login', methods=['GET', 'POST'])
def login():
    current_page = '/login'
    if not session.get('logged_in'):
        if request.method == "POST":
            username = request.form['username']
            password = request.form['password']

            user = User.query.filter_by(username=username).first()

            if user:
                if user.check_password(password):
                    session['username'] = user.username
                    session['logged_in'] = True
                    return redirect('/dashboard')
                else:
                    return "Invalid password"
            else:
                return "User not found"
    else:
        return redirect('/dashboard')
    
    return render_template('auth/login.html', current_page=current_page)

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session['logged_in'] = False
    session.pop('username', None)

    return redirect('/')

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    current_page = '/dashboard'
    weather = None
    response = None

    if session['logged_in'] == False:
        return redirect('/login')
    
    if request.method == 'POST':
        city = request.form['city']
        url = f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={open_weather_token}&units=metric'
        response = requests.get(url).json()
        print(response)
        if response['cod'] != '404':
            weather = {
                'city': city,
                'temperature': round(response['main']['temp'], 1),
                'description': response['weather'][0]['description'],
                'icon': response['weather'][0]['icon']
            }
    
    return render_template('dashboard.html', current_page=current_page, weather=weather, response=response)

if __name__ == '__main__':
    app.run(debug=True)