import sqlite3
from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import bcrypt
import time

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-very-secret-key'

login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    connection = getDBConnection()
    user_data = connection.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    connection.close()
    if user_data:
        return User(id=user_data['id'], username=user_data['username'])
    return None

def initDB():
    with sqlite3.connect('database.db') as connection:
        connection.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, password TEXT)''')
    hashedPassword = bcrypt.hashpw('trythis123'.encode('utf-8'), bcrypt.gensalt())
    try:
        connection.execute('INSERT INTO users (username, password) VALUES (?, ?)', ('admin', hashedPassword))
        connection.commit()
    except sqlite3.IntegrityError:
        pass
    connection.close()

def getDBConnection():
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    return connection

class User(UserMixin):
    def __init__(self, id, username):
        self.id = id
        self.username = username

@app.route('/login', methods=['GET', 'POST'])
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("password")
        connection = getDBConnection()
        user = connection.execute("SELECT * FROM users where username = ?", (username,)).fetchone()
        connection.close()

        if user and bcrypt.checkpw(password.encode('utf-8'), user['password'], ):
            userObject = User(id=user['id'], username=user['username'])
            login_user(userObject)
            if current_user.username == "admin":
                return render_template('dashboard.html', username=user)
            else:
                return render_template('quiz.html')
        else:
            return render_template('login.html', error="Username or password is incorrect!")

    return render_template('login.html',)
    

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

    connection = getDBConnection()
    users = connection.execute('SELECT * FROM users').fetchall()
    connection.close()

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("password")
        
        hashedPassword = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

        connection = getDBConnection()

        try:
            connection.execute('INSERT INTO users (username, password) VALUES (?,?)',(username, hashedPassword)) 
            connection.commit()
            connection.close()
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            connection.close()
            return render_template('register.html', error="Username already exists!")
            
    return render_template('register.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/quiz', methods=['GET', 'POST'])
def quiz():
    pass

if __name__ == '__main__':
    initDB()
    app.run(debug=True)

