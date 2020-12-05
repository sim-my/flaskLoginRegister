from flask import Flask, render_template, redirect,request,url_for,session
from flask_mysqldb import MySQL, MySQLdb
import bcrypt

app = Flask(__name__)
app.secret_key = "5cbb1140af7d3c8cca5dcec8"
app.config['SESSION_TYPE'] = 'filesystem'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_PORT'] = 3307
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'userdb'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)
 
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login', methods=["GET","POST"])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password'].encode('utf-8')

        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute('SELECT * from users WHERE email=%s',[email])
        user = cur.fetchone()
        cur.close()

        if user is not None:
            if(bcrypt.hashpw(password,user['password'].encode('utf-8'))) == user['password'].encode('utf-8'):
                session['name'] = user['name']
                session['email'] = user['email']
                return render_template('home.html')
            else:
                return render_template('login.html',message='Unmatched password')
        else:
            return render_template('login.html',message='No such email is registered.')

    else:
        return render_template('login.html')

@app.route('/register', methods=["GET","POST"])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    else:
        name = request.form['name']
        email = request.form['email']
        password = request.form['password'].encode('utf-8')
        hash_password = bcrypt.hashpw(password, bcrypt.gensalt())

        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute('SELECT * from users WHERE email=%s',[email])
        user = cur.fetchone()
        cur.close()

        print(user)   

        if user is None:
            cur = mysql.connection.cursor()    
            cur.execute("INSERT INTO users (name, email, password) VALUES (%s, %s, %s)",(name,email,hash_password))
            mysql.connection.commit()
            session['name'] = name
            session['email'] = email
            return redirect(url_for("home"))
        else:
            return render_template('register.html',message='Registered user already exists.')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True)