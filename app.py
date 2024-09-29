# Creator: Israel Showell
# Start Date: 9/27/2024
# End Date: /2024
# Project: Tasker - Task Management Application
# Version: 0.01

# Description:
"""
This is the main Python script in the task management web application!
This script calls all the other modules and templates that were used in this program!
This web application allows users to create, log into, and manage an account, add tasks to their dashboard and run common functionalities on the tasks, and mark them complete!
The programming for this project was begun September 27th 2024 and was finished at ==!
"""

#These are the imported libaries I am using to make the program
from flask import Flask, render_template, request, flash
from signupForm import signUpForm
from datetime import datetime
import sqlite3


#Important variables and objects
#Requried by Flask to detect the app when running 'flask run'
app=Flask(__name__)
#This is used to help protect data being sent by the app.
#This protection is used to defend against CSRF attacks.
#(Cross-Site Request Forgery)
app.secret_key="__privatekey__"


#All HTML files are located in the 'templates' because that is where render_template looks for HTML files

#The Home Page is located as the root of the web page
@app.route('/')
def Home():
    #Home is referenced in the HTML files
    return render_template('Home.html')

#End of Home function

#The signup Page is able to detect POST and GET requests
#POST sends data, GET gets data
@app.route('/signup', methods=['POST','GET']) 
def signup():
    #This creates an object named signUp based off of the form defined in the formsubmission module
    signUp = signUpForm()

    #The program connects to the database
    signUp_connection=sqlite3.connect('task-management.db')
    #c serves as a database cursor, a control structure that enables traversal over the records in a database
    manage_cursor=signUp_connection.cursor()

    #When the button is pressed, the user makes the page send a POST request
    if request.method=='POST':
        #Checks to make sure the user didn't leave the Username and Password fields blank
        if(request.form["Username"]!="" and request.form["Password"]!=""):
            #Saves the request's data in variables
            E_mail = request.form['Email']
            userName = request.form['Username']
            passWord = request.form['Password']
            PhoneNumber = request.form['PhoneNumber']
            Gender = request.form['Gender']
            Address = request.form['Address']
            Age = request.form['Age']

            #statement holds an SQL Query for the users table in the users database
            #This query checks to see if the user, password, and email entered exist in the database
            statement=f"SELECT * from users WHERE Username='{userName}' AND Password='{passWord}' AND Email='{E_mail}';"

            #We then tell the cursor to run the query
            manage_cursor.execute(statement)

            #Stores the result of the query in the data variable
            data=manage_cursor.fetchone()

            #If the data matches both the password and username, then the user will be taken to the error page
            if data:
                return render_template("error.html")
            else:
                #If at least the Email, Username, and Password are different from what is in the database
                if not data:
                    #Then the user's information will be added into the database
                    date_created = str(datetime.now())
                    manage_cursor.execute("INSERT INTO users (Email,Username,Password,PhoneNumber,Gender,Address,Age,DateAccountCreated) VALUES (?,?,?,?,?,?,?,?)",(E_mail,userName,passWord,PhoneNumber,Gender,Address,Age,date_created))
                    signUp_connection.commit()
                    signUp_connection.close()
                    #Then they are taken to the login page
                    return render_template("login.html")
                
    #When a user first goes to the register page, the page is rendered with a fresh form
    elif request.method=='GET':
        return render_template('register.html',form=signUp)

#End of Signup function


#The Login Page is able to detect POST and GET requests
#POST sends data, GET gets data
@app.route('/login', methods=['POST','GET'])
def login():
    #When the button is pressed, the user makes the page send a POST request
    if request.method=='POST':
        #Saves the request's data in variables
        userName = request.form['Username']
        passWord = request.form['Password']

        #Then it connects to the database
        login_connection = sqlite3.connect('task-management.db')
        #c serves as a database cursor, a control structure that enables traversal over the records in a database
        manage_cursor = login_connection.cursor()

        #statement holds an SQL Query for the users table in the users database
        #This query checks to see if the user and password entered exist in the database
        statement=f"SELECT * from users WHERE Username='{userName}' AND Password='{passWord}';"

        #We then tell the cursor to run the query
        manage_cursor.execute(statement)
        #manage_cursor.fetchone fetchs the next row of a query resultand returns a single tuple,
        #Or None if no more rows are available.
        if not manage_cursor.fetchone():
            #If the user and password is not found, the program will not sign them in
            return render_template("login.html")
        else:
            #If the login is right, they go to the dashboard page, and their name is displayed
            return render_template('dashboard.html', name=userName)
    else:
        #If the user is just going to the login page, the page is rendered by the program
         request.method=='GET'
         return render_template("login.html")

#End of Login function


# The password reset Page is able to detect POST and GET requests
# POST sends data, GET gets data
@app.route('/reset_password', methods=['POST', 'GET'])
def reset_password():
    
    #Occures when the user presses the submit button
    if request.method == 'POST':
        email = request.form['Email']
        new_password = request.form['NewPassword']
        confirm_password = request.form['ConfirmPassword']
        
        #Checks if both password fields match
        if new_password != confirm_password:
            flash("Passwords do not match!", "error")
            return render_template('reset_password.html')

        #Connects to the database
        reset_connection = sqlite3.connect('task-management.db')
        manage_cursor = reset_connection.cursor()

        #Checks if the email exists in the database
        manage_cursor.execute("SELECT * FROM users WHERE Email=?", (email,))
        user_data = manage_cursor.fetchone()

        #If the user entered a valid email
        if user_data:
            #Updates the user's password in the database
            manage_cursor.execute("UPDATE users SET Password=? WHERE Email=?", (new_password, email))
            reset_connection.commit()
            reset_connection.close()
            
            #This will notify the user that the password has been changed
            flash("Your password has been successfully updated. Please log in with your new password.", "info")
            return render_template('login.html')
        else:
            #If the email is not found
            flash("No account found with that email address.", "error")
            return render_template('reset_password.html')
    #Called on a normal GET request
    return render_template('reset_password.html')

# End of Password Reset function


#This is the start up function that runs when the app is ran in the command line to start
def startup():
    #Connects to the database
    initial_connection = sqlite3.connect('task-management.db')
    #Sets a cursor to each database
    manage_cursor =  initial_connection.cursor()
    #Runs a query to create a table if it does not exist
    #The data parameters that the tables can handle are a text username and a text password, etc
    #PRIMARY KEY automatically adds the UNIQUE constraint!
    manage_cursor.execute("CREATE TABLE IF NOT EXISTS users(User_ID INTEGER PRIMARY KEY, Email text NOT NULL, Username text NOT NULL, Password text NOT NULL, PhoneNumber INTEGER NOT NULL, Gender text NOT NULL, Address text NOT NULL, Age INTEGER NOT NULL, DateAccountCreated text NOT NULL)")
    manage_cursor.execute("CREATE TABLE IF NOT EXISTS tasks(Task_ID INTEGER PRIMARY KEY, TaskName text NOT NULL, TaskDesc text NOT NULL, Importance INTEGER NOT NULL, Urgency INTEGER NOT NULL, TaskDeadline text NOT NULL, DateTaskCreated text NOT NULL, User_ID INTEGER NOT NULL, Username text NOT NULL, FOREIGN KEY(User_ID) REFERENCES users(User_ID), FOREIGN KEY(Username) REFERENCES users(Username))")

    #Then the changes are added to the database
    initial_connection.commit()

#End of Startup function







#This needs to be outside of the __name__ part, because Flask skips over it.
startup()
if __name__=='__main__':
    app.run()

#End of Script
