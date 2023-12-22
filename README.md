This repository contains the HTML pages and back end Python script integreted with Flask of the Lion Auction website used for Bidding, Selling various products.

Required Packages:
Flask
sqlite3
hashlib

Instructions to run:
1. Extract all files from Charlie_Lu_lion_auction.zip inside of a single folder
2. Open lionauction.py in Pycharm Professional
3. Run lionauction.py
4. Click link in output, should be http://127.0.0.1:5000/
5. Interact with wepage at your convenience.

Background/Features:
This web application demostrates the login functionality of the lion auction platform.
There are two main features, login and register. Login takes an email and password which will be
used to check with the database of existing users to verify a correct login combination.
Register will allow a user to add their email and password to the database as a new account.
Passwords are hashed so that they are encrypted and will now show up as legible. For the purposes
of testing and debugging, the original password is also stored along with the hashed version in 
this demo. In the future it will be removed. The database itself is hashed in a separated .ipynb file.

Organization:
The application is build on python and utilizes Flask to execute the SQL queries and display the html
pages on a web browser. 
The application is stored along with the database while the html files are stores in a separate template
folder which is accessed through the render_template package.

