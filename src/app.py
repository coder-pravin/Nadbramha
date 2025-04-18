from flask import Flask, render_template, request, redirect, session, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import mysql.connector

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Change this to something secure in production

# --- Database Connection ---
def get_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Pravyaa@143",  # Add your DB password here
        database="naadbramha_db"
    )

# --- Routes ---

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = generate_password_hash(request.form['password'])

        db = get_db()
        cursor = db.cursor()
        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
        db.commit()
        cursor.close()
        db.close()
        return redirect('/')
    return render_template('register.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    user = cursor.fetchone()
    cursor.close()
    db.close()

    if user and check_password_hash(user['password'], password):
        session['user'] = user['username']
        return redirect('/dashboard')
    return "Invalid credentials. <a href='/'>Try again</a>"

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect('/')
    
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM menu")
    items = cursor.fetchall()
    cursor.close()
    db.close()
    return render_template('dashboard.html', items=items)

@app.route('/invoice', methods=['POST'])
def invoice():
    cart = request.json['cart']
    return render_template('invoice.html', cart=cart)

@app.route('/admin')
def admin():
    if 'user' not in session:
        return redirect('/')
    
    db = get_db()
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM menu")
    items = cursor.fetchall()
    cursor.close()
    db.close()
    return render_template('admin.html', items=items)

@app.route('/add_item', methods=['POST'])
def add_item():
    name = request.form['name']
    price = float(request.form['price'])

    db = get_db()
    cursor = db.cursor()
    cursor.execute("INSERT INTO menu (item_name, price) VALUES (%s, %s)", (name, price))
    db.commit()
    cursor.close()
    db.close()
    return redirect('/admin')


# --- Run the App ---
if __name__ == '__main__':
    print("Starting NaadBramha App...")
    app.run(debug=True)
