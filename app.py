from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
import pymysql

app = Flask(__name__)

# Configure MySQL
db_config = {
    'host': '127.0.0.1',
    'user': 'root',
    'password': '279936',
    'db': 'college_db',
    'cursorclass': pymysql.cursors.DictCursor
}

# Secret key for session
app.secret_key = 'your_secret_key'

# Function to get a MySQL connection
def get_db_connection():
    connection = pymysql.connect(**db_config)
    return connection

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        userid = request.form['userid']
        password = request.form['password']
        connection = get_db_connection()
        with connection.cursor() as cur:
            cur.execute("SELECT * FROM users WHERE userid = %s", (userid, ))
            user = cur.fetchone()

        connection.close()

        if user and check_password_hash(user['password'], password):
            print(user)
            session['userid'] = userid
            session['username'] = user['username']
            flash('Login successful!', 'success')
            return redirect(url_for('welcome'))
        else:
            flash('Login failed. Check your credentials.', 'error')

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        userid = request.form['userid']
        username = request.form['username']
        mobile = request.form['mobile']
        password = request.form['password']
        hashed_password = generate_password_hash(password)

        connection = get_db_connection()
        with connection.cursor() as cur:
            try:
                cur.execute("INSERT INTO users (userid, username, mobile, password) VALUES (%s, %s, %s, %s)", 
                            (userid, username, mobile, hashed_password))
                connection.commit()
                flash('Registration successful!', 'success')
            except Exception as e:
                connection.rollback()
                flash('Registration failed: ' + str(e), 'danger')

        connection.close()
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/welcome')
def welcome():
    if 'userid' in session:
        return render_template('welcome.html', userid=session['userid'], username=session['username'])
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('userid', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))

@app.route('/courses')
def display_courses():
    if 'userid' in session:
        connection = get_db_connection()
        with connection.cursor() as cur:
            cur.execute("SELECT * FROM courses")
            courses = cur.fetchall()
        connection.close()
        
        return render_template('courses.html', courses=courses)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
