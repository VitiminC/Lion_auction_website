from flask import Flask, redirect, url_for, request
from flask import render_template
import sqlite3 as sql
import hashlib

app = Flask(__name__)
host = 'http://127.0.0.1:5000/'


@app.route('/')
# Set default display of webpage to portal.html
def index():
    return render_template('portal.html')


@app.route('/portal', methods=['POST', 'GET'])
# direct user to either add patient or remove patient page depending on option selected
def portal():
    if request.method == 'POST' and request.form['option'] == "Login":
        return redirect(url_for('login'))
    else:
        return redirect(url_for('register'))


# route for the add patient page
@app.route('/register', methods=['POST', 'GET'])
# function for adding a name to database calls valid name function for sql query input
def register():
    error = None
    if request.method == 'POST':
        password = request.form['Password']
        password_check = request.form['Password_check']
        if password != password_check:
            return render_template('failed_register.html')
        else:
            result = valid_name(request.form['Email'], request.form['Password'])
            if result:
                return render_template('login.html', error=error, result=result)
            else:
                error = 'invalid input name'
    # get method for populating the table before taking actions
    #if request.method == 'GET':
        #result = populate_add()
        #if result:
            #return render_template('register.html', error=error, result=result)
    return render_template('register.html', error=error)


# function for running sql query to add name
def valid_name(email, password, pid=1):
    connection = sql.connect('user.sqlite')
    #connection.execute('CREATE TABLE IF NOT EXISTS users(pid INTEGER, UserID TEXT, Password TEXT, Email TEXT);')

    # try function for incrementing the pid by 1 for a unique pid value for each patient not ideal but temporary
    # temporary solution, not ideal
    #try:
        #temp = connection.execute('SELECT MAX(pid) FROM users;')
        #max_pid = temp.fetchone()[0] + 1
    #except:
        #max_pid = pid
    # creates table if non exists with 3 attributes, pid, firstname, lastname
    #connection.execute('INSERT INTO users (pid, userid, password, email) VALUES (?,?,?,?);', (max_pid, userid, password, email))
    encoded_password = password.encode('utf-8')
    hashed_password = hashlib.sha1(encoded_password)
    pass_hex = hashed_password.hexdigest()
    #connection.execute('INSERT INTO hashed_password (email, password, hashed_password) VALUES (?,?,?,?);',(email, password, pass_hex))
    #connection.commit()
    # displays patients in descending order of pid which is also chronologically the most recent patient listed first
    connection.execute('INSERT INTO user_hashed (email, password, hashed_password) VALUES (?,?,?);',(email, password, pass_hex))
    connection.commit()
    cursor = connection.execute('SELECT * FROM user_hashed WHERE email = ? AND password = ? AND hashed_password = ?',(email, password, pass_hex))
    # connection.execute('DROP TABLE users;')
    return cursor.fetchall()


def populate_add():
    connection = sql.connect('user.sqlite')
    cursor = connection.execute('SELECT * FROM Users ORDER BY pid DESC;')
    return cursor.fetchall()


# route for the remove patient page
@app.route('/login', methods=['POST', 'GET'])
# function for removing a name from the database
def login():
    error = None
    if request.method == 'POST':
        result = valid_login(request.form['Email'], request.form['Password'])
        if result == 1:
            return render_template('success.html', error=error, result=result)
        else:
            error = 'invalid Email or Password'
            return render_template('failed.html', error=error, result=result)

    # get method for populating the table before taking actions
    if request.method == 'GET':
        result = populate()
        if result:
            return render_template('login.html', error=error, result=result)

    return render_template('login.html', error=error)


# function for executing sql deletion of name based on first,last name inputs
def valid_login(Email, Password, pid=1):
    encoded_password = Password.encode('utf-8')
    hashed_password = hashlib.sha1(encoded_password)
    pass_hex = hashed_password.hexdigest()
    connection = sql.connect('user.sqlite')
    #connection.execute('SELECT COUNT(1) FROM Users WHERE email = ? AND password = ?;', (Email, Password))
    #connection.commit()
    #cursor = connection.execute('SELECT * FROM users;')
    cursor = connection.execute('SELECT COUNT(email) FROM user_hashed WHERE email = ? AND hashed_password = ?;', (Email, pass_hex))
    return cursor.fetchall()[0][0]


# function for populating existing patient table on removal page
def populate():
    connection = sql.connect('database.db')
    cursor = connection.execute('SELECT * FROM users ORDER BY pid DESC;')
    return cursor.fetchall()


if __name__ == "__main__":
    DEBUG = True
    app.run(debug=DEBUG)
