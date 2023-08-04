from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_session import Session
import sqlite3

app = Flask(__name__)
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
app.secret_key = 'username'

@app.route('/')
def index():
    if 'user_id' in session:
        user_id = session['user_id']
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute('SELECT username FROM users WHERE id = ?', (user_id,))
        username = cursor.fetchone()[0]
        conn.close()
        return render_template('user_page.html', username=username)
    return render_template('index.html', logado=False)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()

        cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
        conn.commit()
        conn.close()
        flash('Usuário criado com sucesso!')
        return redirect(url_for('index'))
    return render_template('register.html')

def init_db():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                password TEXT NOT NULL
            )
        ''')
    conn.commit()
    conn.close()
init_db()

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, username FROM users WHERE username = ? AND password = ?', (username, password))
    user = cursor.fetchone()
    conn.close()

    if user:
        user_id, username = user
        session['user_id'] = user_id  
        flash('Login realizado com sucesso!', 'success')
        return redirect(url_for('index')) 
    else:
        flash('Usuário ou senha incorretos. Por favor, tente novamente.', 'error')
        return redirect(url_for('index'))

@app.route('/logout', methods=['POST'])
def logout():
    session.pop('_flashes', None)
    session.pop('user_id', None)
    flash('Você saiu da sua conta.', 'success')
    return redirect(url_for('index')) 


@app.route('/user_page')
def user_page():
    if 'user_id' in session:
        user_id = session['user_id']
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute('SELECT username FROM users WHERE id = ?', (user_id,))
        username = cursor.fetchone()[0]
        conn.close()
        return render_template('user_page.html', username=username)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
