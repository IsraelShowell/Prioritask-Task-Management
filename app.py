# Creator: Israel Showell
# Start Date: 9/27/2024
# End Date: /2024
# Project: Prioitask - Task Management Application
# Version: 0.40

# Description:
"""
This is the main Python script in the task management web application!
This script calls all the other modules and templates that were used in this program!
This web application allows users to create, log into, and manage an account, add tasks to their dashboard and run common functionalities on the tasks, and mark them complete!
The programming for this project was begun September 27th 2024 and was finished at ==!
"""

#These are the imported libaries I am using to make the program
from flask import Flask, render_template, request, flash, session, redirect, url_for
from signupForm import signUpForm
from datetime import datetime
from math import ceil
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

        #The variable statement holds an SQL Query for the users table in the users database
        #This query checks to see if the user and password entered exist in the database
        statement = "SELECT User_ID FROM users WHERE Username=? AND Password=?;"
        
        #We then tell the cursor to run the query
        manage_cursor.execute(statement, (userName, passWord))
        
        #This gets the user's data (user_id, username)
        user_data = manage_cursor.fetchone()
            
        #manage_cursor.fetchone fetchs the next row of a query resultand returns a single tuple,
        #Or None if no more rows are available.
        if not user_data:
            #If the user and password is not found, the program will not sign them in
            return render_template("login.html")
        
        else:
            print(user_data[0])
            
            #The user's name and ID are stored in the session objects for later retrieval and use
            # If the user exists, store their ID and name in session
            session['user_id'] = user_data[0]
            session['user_name'] = userName
            
            #If the login is right, they go to the dashboard function, and their name is displayed
            request.method = 'GET'
            return dashboard()
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


#This route is used to create and display tasks
@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    
    #This gets the logged-in user’s id from the session object
    user_id = session.get('user_id')
    
    #Ensures the user is logged in
    if not user_id:
        return render_template('login.html', error="Please log in to continue.")
    
    #This gets the logged-in username from the session object
    user_name = session.get('user_name')
    
    #This gets the current page, with the default set to 1
    page = int(request.args.get('page', 1))  
    
    #This limits the number of tasks per page to 10
    tasks_per_page = 10  

    # Task completion logic
    if 'complete_task' in request.form:
        task_id = request.form.get('complete_task')
        complete_task(task_id, user_id)
        

    #This handles task creation if the form is submitted
    if request.method == 'POST' and 'TaskName' in request.form:
        task_name = request.form['TaskName']
        task_desc = request.form['TaskDesc']
        importance = int(request.form['Importance'])
        urgency = int(request.form['Urgency'])
        deadline = request.form['Deadline']
        date_created = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        #This creates the connect to the database
        conn = sqlite3.connect('task-management.db')
        cursor = conn.cursor()
    
        #This inserts the new task into the database
        cursor.execute(
            """INSERT INTO tasks (TaskName, TaskDesc, Importance, Urgency, 
            TaskDeadline, DateTaskCreated, Completed, User_ID) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (task_name, task_desc, importance, urgency, deadline, date_created, "false", user_id)
        )
        conn.commit()
        conn.close()
    
    #These gather the search, sort, and filter parameters from the request
    search_query = request.args.get('search', '')
    sort_by = request.args.get('sort_by', 'DateTaskCreated')
    sort_order = request.args.get('sort_order', 'DESC')
    completed_filter = request.args.get('filter', 'all')

    #This gets the search, sort, and filter clauses from their respective helper functions
    search_clause, search_values = get_search_clause(search_query)  #Search helper function
    sort_query = get_sort_clause(sort_by, sort_order)  #Sort helper function
    filter_clause = get_filter_clause(completed_filter)  #Filter helper function

        
    #Gets the tasks for the current page
    offset = (page - 1) * tasks_per_page
    
    #This creates the connect to the database
    conn = sqlite3.connect('task-management.db')
    cursor = conn.cursor()
    
    #Fetches tasks based on filters, search, and sort
    cursor.execute(
        f"""SELECT Task_ID, TaskName, TaskDesc, Importance, Urgency, TaskDeadline, Completed 
        FROM tasks 
        WHERE User_ID = ? {search_clause} {filter_clause} 
        {sort_query} 
        LIMIT ? OFFSET ?""",
        (user_id, *search_values, tasks_per_page, offset)
    )

    
    #This puts all the tasks in the database for the user in the tasks tuple
    tasks = cursor.fetchall()

    #This gets the total number of tasks to determine the number of pages
    cursor.execute("SELECT COUNT(*) FROM tasks WHERE User_ID=?", (user_id,))
    total_tasks = cursor.fetchone()[0]
    
    #This makes sure that the number of isn't zero should there be no tasks
    if cursor.fetchone():
        total_pages = ceil(total_tasks / tasks_per_page)
    else:
        total_pages = 1

    #This closes the connection to the database
    conn.close()

    #This renders the dashboard with tasks and the page info
    # return render_template('dashboard.html', name=user_name, tasks=tasks, page=page, total_pages=total_pages)
    return render_template(
        'dashboard.html', 
        name=user_name, 
        tasks=tasks, 
        page=page, 
        total_pages=total_pages, 
        search_query=search_query,
        sort_by=sort_by,
        sort_order=sort_order,
        completed_filter=completed_filter
    )

# This route allows the user to update an existing task
@app.route('/update_task', methods=['POST', 'GET'])
def update_task():
    # Get the task ID from query parameters
    task_id = request.args.get('task_id')
    # print(task_id)
    
    # Retrieve the user ID from the session
    user_id = session.get('user_id')
    if not user_id:
        return render_template('dashboard.html', error="You must be logged in.")

    # Connect to the database
    conn = sqlite3.connect('task-management.db')
    cursor = conn.cursor()

    if request.method == 'POST':
        # Retrieve the form data
        task_name = request.form.get('TaskName')
        task_desc = request.form.get('TaskDesc')
        importance = int(request.form.get('Importance'))
        urgency = int(request.form.get('Urgency'))
        deadline = request.form.get('Deadline')

        # Ensure all fields contain data
        if all([task_name, task_desc, importance, urgency, deadline]):
            try:
                # Execute the update query
                cursor.execute(
                    """UPDATE tasks SET TaskName = ?, TaskDesc = ?, Importance = ?, 
                    Urgency = ?, TaskDeadline = ? WHERE Task_ID = ? AND User_ID = ?""",
                    (task_name, task_desc, importance, urgency, deadline, task_id, user_id)
                )
                conn.commit()
                conn.close()
                # print(task_id)
                #Redirects back to the dashboard
                return redirect(url_for('dashboard'))
            except Exception as e:
                conn.rollback()
                return render_template('update_task.html', task_id=task_id, error=f"Error updating task: {e}")
        else:
            return render_template('update_task.html', task_id=task_id, error="All fields are required.")
    else:
        # Pre-fill the form with the existing task data
        cursor.execute(
            """SELECT TaskName, TaskDesc, Importance, Urgency, TaskDeadline 
               FROM tasks WHERE Task_ID = ? AND User_ID = ?""",
            (task_id, user_id)
        )
        task = cursor.fetchone()
        conn.close()
        
        if task:
            # print(task_id)
            return render_template('update_task.html', task=task)
        else:
            return dashboard()


# This route handles the deletion of a task
@app.route('/delete_task', methods=['GET'])
def delete_task():
    # Get the task ID from query parameters
    task_id = request.args.get('task_id')

    # Retrieve the user ID from the session
    user_id = session.get('user_id')
    if not user_id:
        return render_template('dashboard.html', error="You must be logged in.")

    try:
        # Connect to the database and delete the task
        conn = sqlite3.connect('task-management.db')
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM tasks WHERE Task_ID = ? AND User_ID = ?", 
            (task_id, user_id)
        )
        conn.commit()
    except Exception as e:
        print(f"Error occurred: {e}")
        return render_template('dashboard.html', error="Failed to delete task.")
    finally:
        conn.close()

    return dashboard()


#This is a helper function that will fetch the users tasks
def fetch_tasks(user_id):
    conn = sqlite3.connect('task-management.db')
    cursor = conn.cursor()
    cursor.execute(
        "SELECT Task_ID, TaskName, TaskDesc, Importance, Urgency, TaskDeadline "
        "FROM tasks WHERE User_ID = ?", (user_id,)
    )
    tasks = cursor.fetchall()
    conn.close()
    return tasks

#This is a helper function to complete a task
def complete_task(task_id, user_id):
    conn = sqlite3.connect('task-management.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE tasks SET Completed = 'true' WHERE Task_ID = ? AND User_ID = ?", (task_id, user_id))
    conn.commit()
    conn.close()

#This is a helper function for the search functionality
def get_search_clause(search_query):
    
    #This will take whatever is in the search bar and run a query based on it
    if search_query:
        return "AND (TaskName LIKE ? OR TaskDesc LIKE ?)", (f"{search_query}%", f"{search_query}%")
    return "", ()

#This is a helper function for the sort functionality
def get_sort_clause(sort_by, sort_order):
    
    #Tells the program which sort columns are available
    valid_sort_columns = ['TaskName', 'Importance', 'Urgency', 'TaskDeadline', 'DateTaskCreated']
    
    #If one isn't chosen, then this is the default
    if sort_by not in valid_sort_columns:
        sort_by = 'Importance'
        
        #Returns the chosen or default column and the SQLite query
    return f"ORDER BY {sort_by} {sort_order}"

#This is a helper function for the filter functionality
def get_filter_clause(completed_filter):
    
    #Checks if the filter is completed or incomplete
    if completed_filter == 'completed':
        return "AND Completed = 'true'"
    elif completed_filter == 'incomplete':
        return "AND Completed = 'false'"
    return ""

#This is the start up function that runs when the app is ran in the command line to start
def startup():
    #Connects to the database
    initial_connection = sqlite3.connect('task-management.db')
    #Sets a cursor to each database
    manage_cursor =  initial_connection.cursor()
    
    #Runs a query to create a table if it does not exist
    #The data parameters that the tables can handle are a text username and a text password, etc
    #PRIMARY KEY automatically adds the UNIQUE constraint!
    manage_cursor.execute("CREATE TABLE IF NOT EXISTS users(User_ID INTEGER PRIMARY KEY, Email text NOT NULL UNIQUE, Username text NOT NULL UNIQUE, Password text NOT NULL, PhoneNumber INTEGER NOT NULL, Gender text NOT NULL, Address text NOT NULL, Age INTEGER NOT NULL, DateAccountCreated text NOT NULL)")
    manage_cursor.execute("CREATE TABLE IF NOT EXISTS tasks(Task_ID INTEGER PRIMARY KEY, TaskName text NOT NULL, TaskDesc text NOT NULL, Importance INTEGER NOT NULL, Urgency INTEGER NOT NULL, TaskDeadline text NOT NULL, DateTaskCreated text NOT NULL, Completed text NOT NULL, User_ID INTEGER NOT NULL, FOREIGN KEY(User_ID) REFERENCES users(User_ID))")

    #Then the changes are added to the database
    initial_connection.commit()

#End of Startup function


#This needs to be outside of the __name__ part, because Flask skips over it.
startup()
if __name__=='__main__':
    app.run()

#End of Script
