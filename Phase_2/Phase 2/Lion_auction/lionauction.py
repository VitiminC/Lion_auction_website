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
        return render_template('myinfo_vendor.html', routing=routing, bank_num=bank_num, balance=balance)

    else:
        return render_template('myinfo.html', email_address=email)

@app.route('/browse', methods=['POST', 'GET'])
def browse():
    return render_template('browse.html')

#Beauty Products Section
@app.route('/BeautyProducts', methods=['POST', 'GET'])
def BeautyProducts():
    return render_template('BeautyProducts.html')
@app.route('/Makeup', methods=['POST', 'GET'])
def Makeup():
    return render_template('Makeup.html')

#Clothing Section
@app.route('/Clothing', methods=['POST', 'GET'])
def clothing():
    return render_template('clothing.html')
@app.route('/bottoms', methods=['POST', 'GET'])
def bottoms():
    return render_template('bottoms.html')
@app.route('/tops', methods=['POST', 'GET'])
def tops():
    return render_template('tops.html')
@app.route('/sleepwear', methods=['POST', 'GET'])
def sleepwear():
    return render_template('sleepwear.html')

#Electrical
@app.route('/ElectricalSupplies', methods=['POST', 'GET'])
def ElectricalSupplies():
    return render_template('electricalsupplies.html')
@app.route('/cellphones', methods=['POST', 'GET'])
def cellphones():
    return render_template('cellphones.html')
@app.route('/tv', methods=['POST', 'GET'])
def tv():
    return render_template('tv.html')
@app.route('/wearable', methods=['POST', 'GET'])
def wearable():
    return render_template('wearable.html')

#Grocery
@app.route('/grocery', methods=['POST', 'GET'])
def grocery():
    return render_template('grocery.html')
@app.route('/bakery', methods=['POST', 'GET'])
def bakery():
    return render_template('bakery.html')
@app.route('/meat', methods=['POST', 'GET'])
def meat():
    return render_template('meat.html')

#health
@app.route('/PharmacyHealthWellness', methods=['POST', 'GET'])
def PharmacyHealthWellness():
    return render_template('PharmacyHealthWellness.html')
@app.route('/healthcare', methods=['POST', 'GET'])
def healthcare():
    return render_template('healthcare.html')
@app.route('/wellness', methods=['POST', 'GET'])
def wellness():
    return render_template('wellness.html')

#kitchen
@app.route('/Kitchen', methods=['POST', 'GET'])
def Kitchen():
    return render_template('Kitchen.html')
@app.route('/cooking', methods=['POST', 'GET'])
def cooking():
    return render_template('cooking.html')
@app.route('/cabinets', methods=['POST', 'GET'])
def cabinets():
    return render_template('cabinets.html')
@app.route('/sinks', methods=['POST', 'GET'])
def sinks():
    return render_template('sinks.html')

#outdoor
@app.route('/OutdoorDecor', methods=['POST', 'GET'])
def OutdoorDecor():
    return render_template('OutdoorDecor.html')
@app.route('/lighting', methods=['POST', 'GET'])
def lighting():
    return render_template('lighting.html')
@app.route('/furniture', methods=['POST', 'GET'])
def furniture():
    return render_template('furniture.html')
@app.route('/cushions', methods=['POST', 'GET'])
def cushions():
    return render_template('cushions.html')

#pets
@app.route('/Pets', methods=['POST', 'GET'])
def Pets():
    return render_template('Pets.html')
@app.route('/cats', methods=['POST', 'GET'])
def cats():
    return render_template('cats.html')
@app.route('/dogs', methods=['POST', 'GET'])
def dogs():
    return render_template('dogs.html')

#sports
@app.route('/SportsOutdoors', methods=['POST', 'GET'])
def SportsOutdoors():
    return render_template('SportsOutdoors.html')
@app.route('/exercise', methods=['POST', 'GET'])
def exercise():
    return render_template('exercise.html')
@app.route('/sports', methods=['POST', 'GET'])
def sports():
    return render_template('sports.html')
@app.route('/bikes', methods=['POST', 'GET'])
def bikes():
    return render_template('bikes.html')

#toys
@app.route('/ToysVideoGames', methods=['POST', 'GET'])
def ToysVideoGames():
    return render_template('ToysVideoGames.html')
@app.route('/toys', methods=['POST', 'GET'])
def toys():
    return render_template('toys.html')
@app.route('/videogames', methods=['POST', 'GET'])
def videogames():
    return render_template('videogames.html')

#Routed Output Page
@app.route('/filter_output', methods=['POST', 'GET'])
def filter_output():
    if request.method == 'POST':
        category = request.form["category"]
        result = populate(category)
        return render_template('filter_output.html', result=result)
@app.route('/bid', methods=['POST', 'GET'])
def bid():
    if request.method == 'POST' and request.form["bid"] == "bid":
        list_id = request.form['id']
        return render_template('bid.html', id=list_id)

@app.route('/place_bid', methods=['POST', 'GET'])
def place_bid():
    if request.method == 'POST' and request.form["bid"] == "bid":
        list_id = request.form['id']
        max_bid = get_max_bid(list_id)
        if type(max_bid) == int:
            min_bid = max_bid+1
        else:
            min_bid = 0
        bid_id = get_new_bid_id()
        seller_email = get_seller_email(list_id)
        bidder_email = request.cookies.get('email')
        num_bids = get_num_bids(list_id)
        bid_limit = get_bid_limit(list_id)
        bid_list = [str(bid_id), seller_email, str(list_id), bidder_email, str(num_bids), str(bid_limit)]
        bid_string = ','.join(bid_list)
        resp = make_response(render_template('bid.html',
                                             id=list_id, max_bid=max_bid, min_bid=min_bid, num_bids=num_bids, bid_limit=bid_limit))
        resp.set_cookie('bidding', bid_string)
        if num_bids == bid_limit:
            render_template('product_already_sold.html')
        else:
            return resp
    if request.method == 'POST' and request.form["x"] == "x":
        price = request.form['bid']
        bid_string = request.cookies.get('bidding')
        bid_list = bid_string.split(',')
        try:
            bidder_email = request.cookies.get('email')
            prev_email = get_prev_bidder(int(bid_list[2]))
            print(bidder_email)
            print(prev_email)
            if bidder_email == prev_email:
                return render_template('failed_bid.html')
        except:
            pass
        prev_max_bid = get_max_bid(int(bid_list[2]))
        if type(prev_max_bid) != int:
            prev_max_bid = 0
        if int(price) > prev_max_bid:
            resp = make_response(render_template('enter_payment.html'))
            resp.set_cookie('my_price', price)
            return resp
        else:
            return render_template('failed_price.html')

def get_prev_bidder(ide):
    connection = sql.connect('user.sqlite')
    cursor = connection.execute('SELECT Bidder_Email FROM Bids WHERE Bid_Price = (SELECT MAX(Bid_Price) FROM Bids WHERE Listing_ID = ?);', (ide,))
    return cursor.fetchone()[0]

@app.route('/submit_payment', methods=['POST', 'GET'])
def submit_payment():
    if request.method == 'POST' and request.form["x"] == "x":
        email = request.cookies.get('email')
        card_type = request.form['card_type']
        exp_month = request.form['month']
        card_num = request.form['card_num']
        exp_year = request.form['exp_year']
        sec_code = request.form['sec_code']
        input_card = (card_num, card_type, int(exp_month), int(exp_year), int(sec_code), email)
        card = get_card_info(email)
        if card == input_card:
            price = request.cookies.get('my_price')
            bid_string = request.cookies.get('bidding')
            bid_list = bid_string.split(',')
            add_bid(int(bid_list[0]), bid_list[1], int(bid_list[2]), bid_list[3], int(price))
            bid_num = int(bid_list[4])
            bid_limit = int(bid_list[5])
            if (bid_num+1) == bid_limit:
                update_status(int(bid_list[2]))
                return render_template('congratz.html', email=email, item=bid_list[2])
            else:
                return redirect(url_for('my_bids'))
        else:
            return render_template('failed_card.html')
def update_status(id_listing):
    connection = sql.connect('user.sqlite')
    connection.execute('UPDATE Auction_Listings_new SET Status = ? WHERE Listing_ID = ?;',
                       (2, id_listing))
    connection.commit()
    return True
@app.route('/my_bids', methods=['POST', 'GET'])
def my_bids():
    email = request.cookies.get('email')
    result = get_bids(email)
    print(result)
    return render_template('my_bids.html', result=result)
def get_bids(email):
    connection = sql.connect('user.sqlite')
    cursor = connection.execute('SELECT * FROM Bids WHERE Bidder_Email = ?;', (email,))
    return cursor.fetchall()
def get_card_info(email):
    connection = sql.connect('user.sqlite')
    cursor = connection.execute('SELECT * FROM Credit_Cards WHERE Owner_Email = ?;', (email,))
    return cursor.fetchall()[0]
def add_bid(bid_id, seller_email, listing_id, bidder_email, bid_price):
    connection = sql.connect('user.sqlite')
    connection.execute('INSERT INTO Bids (Bid_ID, Seller_Email, Listing_ID, Bidder_Email, Bid_Price) VALUES (?,?,?,?,?);',
                       (bid_id, seller_email, listing_id, bidder_email, bid_price))
    connection.commit()
    return True

def get_seller_email(id):
    connection = sql.connect('user.sqlite')
    cursor = connection.execute('SELECT Seller_Email FROM Auction_Listings_new WHERE Listing_ID=?;', (id,))
    return cursor.fetchone()[0]
def get_new_bid_id():
    connection = sql.connect('user.sqlite')
    cursor = connection.execute('SELECT MAX(Bid_ID) FROM Bids;')
    max_id = cursor.fetchone()[0] + 1
    return max_id
def get_max_bid(id):
    connection = sql.connect('user.sqlite')
    cursor = connection.execute('SELECT MAX(Bid_Price) FROM Bids WHERE Listing_ID = ?;', (id,))
    return cursor.fetchone()[0]
def get_num_bids(id):
    connection = sql.connect('user.sqlite')
    cursor = connection.execute('SELECT COUNT(*) FROM Bids WHERE Listing_ID = ?;', (id,))
    return cursor.fetchone()[0]
def get_bid_limit(id):
    connection = sql.connect('user.sqlite')
    cursor = connection.execute('SELECT Max_bids FROM Auction_listings_new WHERE Listing_ID = ?;', (id,))
    return cursor.fetchone()[0]


#seller listing pages
@app.route('/my_listings', methods=['POST', 'GET'])
def my_listings():
    email = request.cookies.get('email')
    listings = populate_listings(email)
    return render_template('my_listings.html', result=listings)

@app.route('/create_listing', methods=['POST', 'GET'])
def create_listing():
    email = request.cookies.get('email')
    return render_template('create_listing.html', email=email)

@app.route('/remove_listing', methods=['POST', 'GET'])
def remove_listing():
    if request.method == 'POST':
        email = request.cookies.get('email')
        listing_id = request.form["id"]
        reason = request.form['reason']
        delete_listings(listing_id, email, reason)
        return redirect(url_for('my_listings'))

@app.route('/update_listing', methods=['POST', 'GET'])
def update_listing():
    if request.method == 'POST':
        email = request.cookies.get('email')
        listing_id = request.form["id"]
        result = get_listing(listing_id, email)
        status = result[0][9]
        if status == 0:
            return render_template('error_completed.html')
        else:
            category = result[0][2]
            title = result[0][3]
            name = result[0][4]
            description = result[0][5]
            quantity = result[0][6]
            reserve = result[0][7]
            return render_template('update.html', category=category, title=title, name=name, description=description, quantity=quantity, reserve=reserve, id=listing_id)

@app.route('/updater', methods=['POST', 'GET'])
def updater():
    if request.method == 'POST':
        email = request.cookies.get('email')
        id_value = request.form['id']
        category = request.form['category']
        title = request.form['auction_title']
        description = request.form['product_description']
        name = request.form['product_name']
        quantity = request.form['quantity']
        reserve_price = request.form['reserve_price']
        update(id_value, email, category, title, name, description, quantity, reserve_price)
        return redirect(url_for('my_listings'))

@app.route('/generate_listing', methods=['POST', 'GET'])
def generate_listing():
    if request.method == 'POST':
        email = request.cookies.get('email')
        id = get_max_id()
        category = request.form['category']
        title = request.form['auction_title']
        description = request.form['product_description']
        name = request.form['product_name']
        quantity = request.form['quantity']
        reserve_price = request.form['reserve_price']
        max_bids = 0
        status = 1
        connection = sql.connect('user.sqlite')
        connection.execute('INSERT INTO Auction_Listings_new (Seller_Email, Listing_ID, Category, Auction_Title, Product_Name, Product_Description, Quantity, Reserve_Price, Max_bids, Status) VALUES (?,?,?,?,?,?,?,?,?,?);',
                           (email, id, category, title, name, description, quantity, reserve_price, max_bids, status))
        connection.commit()

        return redirect(url_for('my_listings'))

def get_listing(id,email):
    connection = sql.connect('user.sqlite')
    cursor = connection.execute('SELECT * FROM Auction_Listings_new WHERE Listing_ID = ? AND Seller_Email = ? ORDER BY Status;', (id,email))
    return cursor.fetchall()

def get_max_id():
    connection = sql.connect('user.sqlite')
    temp = connection.execute('SELECT MAX(Listing_ID) FROM Auction_Listings_new;')
    max_id = temp.fetchone()[0] + 1
    return max_id

def get_max_bids(id):
    connection = sql.connect('user.sqlite')
    temp = connection.execute('SELECT MAX(Listing_ID) FROM Auction_Listings_new;')
    max_id = temp.fetchone()[0] + 1
    return max_id

def delete_listings(id,email,reason):
    connection = sql.connect('user.sqlite')
    connection.execute('UPDATE Auction_Listings_new SET Auction_Title = ?, Product_Description = ?, Status = 0 WHERE Listing_ID = ? AND Seller_Email = ?',
                       ("Removed", reason, id, email))
    #connection.execute('DELETE FROM Auction_Listings_new WHERE Listing_ID = ? AND Seller_Email = ?;', (id, email))
    connection.commit()
    return True

def update(id,email,category, title, name, desc, quantity, price):
    connection = sql.connect('user.sqlite')
    connection.execute('UPDATE Auction_Listings_new SET Category = ?, Auction_Title = ?, Product_Name = ?, Product_Description = ?, Quantity = ?, Reserve_price = ? '
                       'WHERE Listing_ID = ? AND Seller_Email = ?',
                       (category, title, name, desc, quantity, price, id, email))
    connection.commit()
    return True

def populate_listings(email):
    connection = sql.connect('user.sqlite')
    cursor = connection.execute('SELECT * FROM Auction_Listings_new WHERE Seller_Email = ? ORDER BY Status;', (email,))
    return cursor.fetchall()

def valid_login(Email, Password, pid=1):
    encoded_password = Password.encode('utf-8')
    hashed_password = hashlib.sha1(encoded_password)
    pass_hex = hashed_password.hexdigest()
    connection = sql.connect('user.sqlite')
    cursor = connection.execute('SELECT COUNT(email) FROM user_hashed WHERE email = ? AND hashed_password = ?;', (Email, pass_hex))
    return cursor.fetchall()[0][0]

def populate(category):
    connection = sql.connect('user.sqlite')
    cursor = connection.execute('SELECT * FROM Auction_Listings_new WHERE Category = ? AND Status == 1 ORDER BY Reserve_Price ASC;',(category,))
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
