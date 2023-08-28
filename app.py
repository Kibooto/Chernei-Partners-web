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

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    comments = db.Column(db.Text)
    done = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Зовнішній ключ

    def __init__(self, title, comments, user_id):
        self.title = title
        self.comments = comments
        self.user_id = user_id

@app.route('/', methods=['GET', 'POST'])
def index():
    current_page = '/'
    return render_template('index.html', current_page=current_page)

@app.route('/register', methods=['GET', 'POST'])
def register():
    current_page = '/register'
    errors = []
    print(session, errors)
    if not session.get('logged_in'):
        if request.method == 'POST':
            if not request.form['useremail']:
                errors.append('Email is required')
            else:
                useremail = request.form['useremail']
            
            if not request.form['username']:
                errors.append('Username is required')
            else:
                username = request.form['username']
            
            if not request.form['password']:
                errors.append('Password is required')
            else:
                password = request.form['password']
            
            if not request.form['passwordc']:
                errors.append('Confirm password is required')
            else:
                if request.form['passwordc'] != request.form['password'] and request.form['password'] != '':
                    errors.append('Passwords do not match')
            print(errors)
            if not errors:
                new_user = User(useremail=useremail, username=username, password=password)
                db.session.add(new_user)
                db.session.commit()

                return redirect('/login')
            else:
                return render_template('auth/register.html', errors=errors, current_page=current_page)

        return render_template('auth/register.html', current_page=current_page, errors=errors)
    else:
        return redirect('/dashboard')

@app.route('/login', methods=['GET', 'POST'])
def login():
    current_page = '/login'
    errors = []

    if not session.get('logged_in'):
        if request.method == "POST":
            username = request.form['username']
            password = request.form['password']

            user = User.query.filter_by(username=username).first()

            if user and user.check_password(password):
                session['username'] = user.username
                session['logged_in'] = True
                return redirect('/dashboard')
            else:
                errors.append('Invalid')
    else:
        return redirect('/dashboard')
    print(errors)
    return render_template('auth/login.html', current_page=current_page, errors=errors)

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

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    current_page = '/profile'
    return render_template('profile.html', current_page=current_page)

@app.route('/todo', methods=['GET', 'POST'])
def todo():
    current_page = '/todo'
    error = None
    if not session.get('logged_in'):
        return redirect('/login')
    
    user_id = User.query.filter_by(username=session['username']).first().id

    user_todos = Todo.query.filter_by(user_id=user_id).all()

    if request.method == 'POST':
        if not request.form['title']:
            error = 'Title is required'
        if not error:
            title = request.form['title']
            comments = request.form['comments']
            new_todo = Todo(title=title, comments=comments, user_id=user_id)
            db.session.add(new_todo)
            db.session.commit()
            return redirect('/todo')
        else:
            return render_template('todo/todo.html', current_page=current_page, error=error, user_todos=user_todos)

    return render_template('todo/todo.html', current_page=current_page, user_todos=user_todos)

if __name__ == '__main__':
    app.run(debug=True)