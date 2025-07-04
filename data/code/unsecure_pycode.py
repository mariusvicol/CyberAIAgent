import sqlite3
from flask import Flask, request
import os

app = Flask(__name__)

# Hardcoded secret key (vulnerabilitate)
app.config['SECRET_KEY'] = 'supersecret123'

# Vulnerabilitate SQL Injection
@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
    cursor.execute(query)
    result = cursor.fetchone()
    if result:
        return "Login successful"
    else:
        return "Invalid credentials"

# Vulnerabilitate de execuție arbitrară
@app.route('/run', methods=['POST'])
def run():
    command = request.form['cmd']
    os.system(command)  # ⛔️ permite comenzi periculoase (command injection)
    return "Command executed"
