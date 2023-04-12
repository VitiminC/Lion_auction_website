from flask import Flask, redirect, url_for, request, make_response
from flask import render_template
import sqlite3 as sql
import hashlib

app = Flask(__name__)
host = 'http://127.0.0.1:5000/'

@app.route('/')
# Set default display of webpage to portal.html
def index():
    return render_template('portal.html')

@app.route('/go_back')
def go_back():
    return render_template('success.html')

@app.route('/portal', methods=['POST', 'GET'])
def portal():
    if request.method == 'POST' and request.form['option'] == "Login":
        return redirect(url_for('login'))
    else:
        return redirect(url_for('register'))

@app.route('/register', methods=['POST', 'GET'])
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
    return render_template('register.html', error=error)

def valid_name(email, password, pid=1):
    connection = sql.connect('user.sqlite')
    encoded_password = password.encode('utf-8')
    hashed_password = hashlib.sha1(encoded_password)
    pass_hex = hashed_password.hexdigest()
    connection.execute('INSERT INTO user_hashed (email, password, hashed_password) VALUES (?,?,?);',(email, password, pass_hex))
    connection.commit()
    cursor = connection.execute('SELECT * FROM user_hashed WHERE email = ? AND password = ? AND hashed_password = ?',(email, password, pass_hex))
    return cursor.fetchall()

def populate_add():
    connection = sql.connect('user.sqlite')
    cursor = connection.execute('SELECT * FROM Users ORDER BY pid DESC;')
    return cursor.fetchall()

@app.route('/login', methods=['POST', 'GET'])
def login():
    error = None
    if request.method == 'POST':
        result = valid_login(request.form['Email'], request.form['Password'])
        stored = request.form['Email']
        if result == 1:
            resp = make_response(render_template('success.html'))
            resp.set_cookie('email', stored)
            return resp
        else:
            error = 'invalid Email or Password'
            return render_template('failed.html', error=error)

    # get method for populating the table before taking actions
    if request.method == 'GET':
        result = populate()
        if result:
            return render_template('login.html', error=error, result=result)

    return render_template('login.html', error=error)

@app.route('/myinformation', methods=['POST', 'GET'])
def myinformation():
    email = request.cookies.get('email')
    if is_local_vendor(email) == 1:
        info = get_vendor_info(email)
        email_address = info[0][0]
        name = info[0][1]
        phone = info[0][3]
        address = get_address(info[0][2])
        zip_info = get_zip_info(address[0][1])
        zipcode = zip_info[0][0]
        city = zip_info[0][1]
        state = zip_info[0][2]
        street_num = address[0][2]
        street_name = address[0][3]
        seller = get_seller_info(email)
        routing = seller[0][1]
        bank_num = seller[0][2]
        balance = seller[0][3]
        return render_template('myinfo_vendor.html', zip=zipcode, street_num=street_num, street_name=street_name,
                                email_address=email_address, name=name, city=city, state=state,
                                routing=routing, bank_num=bank_num, balance=balance, phone=phone)

    if is_seller(email) == 1 and is_bidder(email) == 1 and is_lsu(email):
        info = populate_info(email)
        address = get_address(info[0][5])
        zip_info = get_zip_info(address[0][1])
        zipcode = zip_info[0][0]
        city = zip_info[0][1]
        state = zip_info[0][2]
        street_num = address[0][2]
        street_name = address[0][3]
        first_name = info[0][1]
        last_name = info[0][2]
        gender = info[0][3]
        age = info[0][4]
        major = info[0][6]
        credit = get_credit_info(email)
        card_num = credit[0][0][-4:]
        card_type = credit[0][1]
        card_exp_month = credit[0][2]
        card_exp_year = credit[0][3]
        security_code = credit[0][4]
        seller = get_seller_info(email)
        routing = seller[0][1]
        bank_num = seller[0][2]
        balance = seller[0][3]
        return render_template('myinfo_seller.html', zip=zipcode, street_num=street_num, street_name=street_name,
                                email_address=email, first_name=first_name, last_name=last_name,
                                gender=gender, age=age, major=major, city=city, state=state, card_num=card_num,
                                card_exp_month=card_exp_month, card_exp_year=card_exp_year, card_type=card_type,
                                security_code=security_code, routing=routing, bank_num=bank_num, balance=balance)

    if is_seller(email) == 1 and is_bidder(email) == 0:
        seller = get_seller_info(email)
        routing = seller[0][1]
        bank_num = seller[0][2]
        balance = seller[0][3]
        return render_template('myinfo_seller.html', email_address=email, routing=routing, bank_num=bank_num, balance=balance)

    if is_lsu(email) and is_bidder(email) == 1:
        info = populate_info(email)
        address = get_address(info[0][5])
        zip_info = get_zip_info(address[0][1])
        zipcode = zip_info[0][0]
        city = zip_info[0][1]
        state = zip_info[0][2]
        street_num = address[0][2]
        street_name = address[0][3]
        first_name = info[0][1]
        last_name = info[0][2]
        gender = info[0][3]
        age = info[0][4]
        major = info[0][6]
        credit = get_credit_info(email)
        card_num = credit[0][0][-4:]
        card_type = credit[0][1]
        card_exp_month = credit[0][2]
        card_exp_year = credit[0][3]
        security_code = credit[0][4]
        return render_template('myinfo.html', zip=zipcode, street_num=street_num, street_name=street_name,
                                email_address=email, first_name=first_name, last_name=last_name,
                                gender=gender, age=age, major=major, city=city, state=state, card_num=card_num,
                                card_exp_month=card_exp_month, card_exp_year=card_exp_year, card_type=card_type,
                                security_code=security_code)

    if not is_lsu(email) and is_bidder(email) == 1:
        credit = get_credit_info(email)
        card_num = credit[0][0][-4:]
        card_type = credit[0][1]
        card_exp_month = credit[0][2]
        card_exp_year = credit[0][3]
        security_code = credit[0][4]
        return render_template('myinfo.html', email_address=email, card_num=card_num,
                                card_exp_month=card_exp_month, card_exp_year=card_exp_year, card_type=card_type,
                                security_code=security_code)

    if not is_lsu(email) and is_seller(email) == 1:
        seller = get_seller_info(email)
        routing = seller[0][1]
        bank_num = seller[0][2]
        balance = seller[0][3]
        return render_template('myinfo_vendor.html', zip=zipcode, street_num=street_num, street_name=street_name,
                                email_address=email_address, name=name, city=city, state=state,
                                routing=routing, bank_num=bank_num, balance=balance, phone=phone)

    else:
        return render_template('myinfo.html', email_address=email)


def valid_login(Email, Password, pid=1):
    encoded_password = Password.encode('utf-8')
    hashed_password = hashlib.sha1(encoded_password)
    pass_hex = hashed_password.hexdigest()
    connection = sql.connect('user.sqlite')
    cursor = connection.execute('SELECT COUNT(email) FROM user_hashed WHERE email = ? AND hashed_password = ?;', (Email, pass_hex))
    return cursor.fetchall()[0][0]

def populate():
    connection = sql.connect('database.db')
    cursor = connection.execute('SELECT * FROM users ORDER BY pid DESC;')
    return cursor.fetchall()

def is_bidder(email):
    connection = sql.connect('user.sqlite')
    cursor = connection.execute('SELECT count(*) FROM Bidders WHERE email = ?;',(email,))
    return cursor.fetchall()[0][0]
def populate_info(email):
    connection = sql.connect('user.sqlite')
    cursor = connection.execute('SELECT * FROM Bidders WHERE email = ?;',(email,))
    return cursor.fetchall()

def get_address(id):
    connection = sql.connect('user.sqlite')
    cursor = connection.execute('SELECT * FROM Address WHERE address_id = ?;',(id,))
    return cursor.fetchall()

def get_zip_info(zip):
    connection = sql.connect('user.sqlite')
    cursor = connection.execute('SELECT * FROM Zipcode_info WHERE zipcode = ?;', (zip,))
    return cursor.fetchall()

def get_credit_info(email):
    connection = sql.connect('user.sqlite')
    cursor = connection.execute('SELECT * FROM Credit_Cards WHERE Owner_email = ?;', (email,))
    return cursor.fetchall()

def is_seller(email):
    connection = sql.connect('user.sqlite')
    cursor = connection.execute('SELECT Count(email) FROM Sellers WHERE email = ?;', (email,))
    return cursor.fetchall()[0][0]

def is_local_vendor(email):
    connection = sql.connect('user.sqlite')
    cursor = connection.execute('SELECT Count(email) FROM Local_Vendors WHERE Email = ?;', (email,))
    return cursor.fetchall()[0][0]

def get_vendor_info(email):
    connection = sql.connect('user.sqlite')
    cursor = connection.execute('SELECT * FROM Local_Vendors WHERE Email = ?;', (email,))
    return cursor.fetchall()

def get_seller_info(email):
    connection = sql.connect('user.sqlite')
    cursor = connection.execute('SELECT * FROM Sellers WHERE email = ?;', (email,))
    return cursor.fetchall()

def is_lsu(email):
    if email[-7:] == 'lsu.edu':
        return True
    else:
        return False

if __name__ == "__main__":
    DEBUG = True
    app.run(debug=DEBUG)
