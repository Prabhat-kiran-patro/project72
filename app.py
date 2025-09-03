from flask import Flask, render_template, request, url_for, redirect, flash, session
import mysql.connector as mys
from werkzeug.security import generate_password_hash, check_password_hash

db_details = {
    'user':'root',
    'host':'localhost',
    'password':'123456',
    'database':'mydata'
}
def connectdb():
    try:
        connection = mys.connect(**db_details)
        return connection
    except:
        print("connection error!")
        return None

def init_db():
    connection = connectdb()
    if connection:
        cursor = connection.cursor()

        create_table_query = """
        create table if not exists users(
        id int auto_increment primary key,
        name varchar(50) not null,
        email varchar(50) not null,
        password_hash varchar(255) not null,
        created_at timestamp default current_timestamp
        )
        """

        cursor.execute(create_table_query)
        connection.commit()
        cursor.close()
        connection.close()

app = Flask(__name__)
app.secret_key = 'a-super-secret-and-random-string-for-my-app'

@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    alert=None
    if request.method=='POST':
        email=request.form.get('email')
        pswd=request.form.get('pswd')

        connection = connectdb()
        if not connection:
            alert='Database connection error'
            return render_template('login.html', alert_message=alert)
        cursor = connection.cursor()

        # checking if user exists
        check_query = "select password_hash, name from users where email=%s"
        cursor.execute(check_query, (email,))
        user = cursor.fetchone()
        if not user:
            alert='User does not exist! Create an account.'
            cursor.close()
            connection.close()
            return render_template('signup.html', alert_message=alert)
        cursor.close()
        connection.close()
        if check_password_hash(user[0], pswd):
            session['user'] = user[1]
            return redirect(url_for('home', user=session['user']))
        else:
            alert="Wrong password"
            return render_template('login.html', alert_message=alert)
    return render_template('login.html', alert_message=alert)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    alert=None
    if request.method == 'POST':
        name = request.form.get('name').strip()
        email = request.form.get('email').strip().lower()
        password = request.form.get('pswd')

        connection = connectdb()
        if not connection:
            alert="Database connection error"
            render_template('signup.html', alert_message=alert)
        cursor = connection.cursor()

        # checking if user already exists
        check_query = "select id from users where email=%s"
        cursor.execute(check_query, (email,))
        user_exists = cursor.fetchone()
        if user_exists:
            alert="User with email already exists"
            cursor.close()
            connection.close()
            return render_template('signup.html', alert_message=alert)
        
        # creating new user
        password_hash = generate_password_hash(password)
        insert_query = """
        insert into users (name, email, password_hash)
        values (%s, %s, %s)
        """
        try:
            cursor.execute(insert_query, (name, email, password_hash))
            connection.commit()
            cursor.close()
            connection.close()
            return render_template('login.html')
        except:
            alert="Error creating account"
            cursor.close()
            connection.close()
            return render_template('signup.html', alert_message=alert)

    return render_template('signup.html', alert_message=alert)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/home')
def home():
    print(f"{session}")
    if 'user' not in session:
        return redirect('/login')
    else:
        return render_template('dash.html', user=session['user'])

if __name__=="__main__":
    init_db()
    app.run(debug=True)