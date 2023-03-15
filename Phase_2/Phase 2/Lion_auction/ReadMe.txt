Required Packages:
Flask
sqlite3

Instructions to run:
1. Extract all files from Charlie_Lu_WPE.zip inside of a single folder
2. Open app.py in Pycharm Professional
3. Run app.py
4. Click link in output, should be http://127.0.0.1:5000/
5. Interact with wepage at your convenience.

Background/Features:
This web based application was created per an assignment in CMPSC 431w at Penn State University.
The purpose of this application is to store patient information for a hospital. The page has two
main functions, add patient and remove patient.
The add patient function allowed for the user to input a first and last name into the database.
The application will then automatically generate an unique integer patient ID.
This ID is comuted by taking the largest current ID value and adding a 1, this ensures unique values.
THe remove patient function is similar to the add patient one, but instead of adding the patient it
removes them from the database. A confirmation pop-up will display for both of these features.

Organization:
The application is build on python and utilizes Flask to execute the SQL queries and display the html
pages on a web browser. 
The application is stored along with the database while the html files are stores in a separate template
folder which is accessed through the render_template package.




