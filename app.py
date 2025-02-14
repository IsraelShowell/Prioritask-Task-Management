# Creator: Israel Showell
# Start Date: 9/27/2024
# End Date: 12/7/2024
# Project: Prioitask - Task Management Application
# Version: 1.01

# Description:
"""
This is the main Python script in the task management web application!
This script calls all the other modules and templates that were used in this program!
This web application allows users to create, log into, and manage an account, add tasks to their dashboard and run common functionalities on the tasks, and mark them complete!
The programming for this project was begun September 27th 2024 and was finished at ==!
"""

#These are the imported libaries I am using to make the program
from flask import Flask, render_template, request, flash, session, redirect, url_for, jsonify
import re  # Regular expressions for password validations
from signupForm import signUpForm
from datetime import datetime
from math import ceil
import sqlite3
from huggingface_hub import InferenceClient
import json
import os
from huggingface_hub import login




#Important variables and objects
#Requried by Flask to detect the app when running 'flask run'
app=Flask(__name__)
#This is used to help protect data being sent by the app.
#This protection is used to defend against CSRF attacks.
#(Cross-Site Request Forgery)
app.secret_key="__privatekey__"

#Defines the Hugging Face model that will be used (TinyLlama in this case)
os.environ['HF_TOKEN'] = "your_token"
login(token="your_token")


#Change this to use a different model
repo_id = "microsoft/Phi-3.5-mini-instruct"

# Initialize the InferenceClient
llm_client = InferenceClient(
    model=repo_id,
    timeout=120,
)


#All HTML files are located in the 'templates' because that is where render_template looks for HTML files
@app.route('/ask_taski', methods=['POST'])
def ask_taski():
    
    data = request.json
    task = data.get('task', {})  # Now assumes a single task dictionary
    query = data.get('question', '')

    print(data)  # Debugging the incoming JSON payload
    print(type(data))  # Ensure it's a dictionary

    print(task) #Prints out all of the task information
    print(type(task)) #List
    
    print(query) #Prints out selected query
    print(type(query)) #String
    
    #This calls the taski function and returns the AI's response
    response = Taski(task, query)

    return jsonify({'response': response})



# Function to call the model and generate a response
def call_llm(inference_client: InferenceClient, prompt: str):
    try:
        response = inference_client.post(
            json={
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": 185,
                    "temperature": 0.2,
                    "top_p": 0.8,
                },
                "task": "text-generation",
            },
        )
        # Decode and parse the response
        generated_text = json.loads(response.decode())[0]["generated_text"]
        
        #Splits at "Response:" to extract only the relevant part
        if "Response:" in generated_text:
            return generated_text.split("Response:", 1)[1].strip()
        return generated_text.strip()  # Fallback if no marker found
    except Exception as e:
        print(f"Error in LLM call: {e}")
        return "Error in generating response."
#End of Call_LLM function

def Taski(task, query):
    # Extracting task details
    task_name = task[1]
    task_desc = task[2]
    task_priority = task[3]
    task_ranking = task[4]
    task_deadline = task[5]
    task_completed = task[6]

    # Create the prompt with a clear marker
    prompt = f"""
    Task Name: {task_name}
    Description: {task_desc}
    Priority: {task_priority}
    Ranking: {task_ranking}
    Deadline: {task_deadline}
    Completed: {task_completed}

    Please respond friendly, briefly, and directly to the following query:
    Query: {query}
    
    Make sure to consider the task's name and description in your response!
    Response:
    """

    # Call the LLM and get only the response
    response = call_llm(llm_client, prompt)
    return response or "No valid response generated."
#End of Taski function


@app.route('/faq')
def faq():
    return render_template('faq.html')

#The Home Page is located as the root of the web page
@app.route('/')
def Home():
    #Home is referenced in the HTML files
    return render_template('Home.html')

#End of Home function

#The signup Page is able to detect POST and GET requests
#POST sends data, GET gets data
#This route is used to connect the user to the registration page
@app.route('/signup', methods=['POST', 'GET'])
def signup():
    #Brings in the class from signUpForm
    signUp = signUpForm()

    # Connect to the database
    signUp_connection = sqlite3.connect('task-management.db')
    manage_cursor = signUp_connection.cursor()

    # The signup page is rendered when a GET request is made
    if request.method == 'POST':
        username = request.form["Username"]
        password = request.form["Password"]
        email = request.form['Email']

        #Runs the Password validation
        if not validate_password(password):
            flash("Password must be at least 8 characters long and contain at least one number and one special character.")
            return render_template('register.html', form=signUp)

        if username and password:
            # Check if email already exists
            manage_cursor.execute("SELECT * FROM users WHERE Email = ?", (email,))
           
            data = manage_cursor.fetchone()

            manage_cursor.execute("SELECT * FROM users WHERE Username = ?", (username,))
             
            data2 = manage_cursor.fetchone()
            # If the email already exists, display an error message
            if data or data2:
                signUp_connection.close()
                return render_template("error.html")
            else:
                #Adds the new user
                date_created = str(datetime.now())
                manage_cursor.execute("INSERT INTO users (Email, Username, Password, DateAccountCreated) VALUES (?, ?, ?, ?)",
                                      (email, username, password, date_created))
                signUp_connection.commit()
                signUp_connection.close()
                return render_template("login.html")
    elif request.method == 'GET':
        return render_template('register.html', form=signUp)

#Checks if the user's password is correct
def validate_password(password):
    """Validates the password against specified criteria."""
    if (len(password) >= 8 and
        re.search(r'\d', password) and
        re.search(r'[!@#$%^&*(),.?":{}|<>]', password)):
        return True
    return False


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
            #print(user_data[0])
            
            #The user's name and ID are stored in the session objects for later retrieval and use
            # If the user exists, store their ID and name in session
            session['user_id'] = user_data[0]
            session['user_name'] = userName
            
            #If the login is right, they go to the dashboard function, and their name is displayed
            request.method = 'GET'
            return redirect(url_for('dashboard'))
    else:
        #If the user is just going to the login page, the page is rendered by the program
         request.method=='GET'
         return render_template("login.html")

#End of Login function


# The password reset Page is able to detect POST and GET requests
# POST sends data, GET gets data
@app.route('/reset_password', methods=['POST', 'GET'])
def reset_password():
    # Occurs when the user presses the submit button
    if request.method == 'POST':
        email = request.form['Email']
        new_password = request.form['NewPassword']
        confirm_password = request.form['ConfirmPassword']
        
        # Checks if both password fields match
        if new_password != confirm_password:
            flash("Passwords do not match!", "error")
            return render_template('reset_password.html')

        # Validate the new password
        if not validate_password(new_password):
            flash("New password must be at least 8 characters long and contain at least one number and one special character.", "error")
            return render_template('reset_password.html')

        # Connects to the database
        reset_connection = sqlite3.connect('task-management.db')
        manage_cursor = reset_connection.cursor()

        # Checks if the email exists in the database
        manage_cursor.execute("SELECT * FROM users WHERE Email=?", (email,))
        user_data = manage_cursor.fetchone()

        # If the user entered a valid email
        if user_data:
            # Updates the user's password in the database
            manage_cursor.execute("UPDATE users SET Password=? WHERE Email=?", (new_password, email))
            reset_connection.commit()
            reset_connection.close()
            
            # This will notify the user that the password has been changed
            flash("Your password has been successfully updated. Please log in with your new password.", "info")
            return render_template('login.html')
        else:
            # If the email is not found
            flash("No account found with that email address.", "error")
            return render_template('reset_password.html')
        
    # Called on a normal GET request
    return render_template('reset_password.html')

# End of Password Reset function

# End of Password Reset function


#This route is used to create and display tasks
@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    
    # Get the logged-in user’s ID from the session object
    user_id = session.get('user_id')
    
    # Ensure the user is logged in
    if not user_id:
        return render_template('login.html', error="Please log in to continue.")
    
    # Get the logged-in username from the session object
    user_name = session.get('user_name')
    
    # Get the current page, with the default set to 1
    page = int(request.args.get('page', 1))  
    
    # Limit the number of tasks per page
    tasks_per_page = 3  

    # Task completion logic
    if 'complete_task' in request.form:
        task_id = request.form.get('complete_task')
        complete_task(task_id, user_id)
        

    # Task creation logic
    if request.method == 'POST' and 'TaskName' in request.form:
        task_name = request.form['TaskName']
        task_desc = request.form['TaskDesc']
        priority = request.form['Priority'] 
        ranking = int(request.form['Ranking'])
        deadline = request.form['Deadline']
        date_created = datetime.now().strftime('%m-%d-%Y %H:%M:%S')

        conn = sqlite3.connect('task-management.db')
        cursor = conn.cursor()

        # Insert task with Priority as a descriptive string and Ranking as an integer
        cursor.execute(
            """INSERT INTO tasks (TaskName, TaskDesc, Priority, Ranking, 
            TaskDeadline, DateTaskCreated, Completed, User_ID) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (task_name, task_desc, priority, ranking, deadline, date_created, "false", user_id)
        )
        
        conn.commit()
        conn.close()

      
    # Gather search, sort, and filter parameters from the request
    search_query = request.args.get('search', '')
    sort_by = request.args.get('sort_by', 'Priority')
    sort_order = request.args.get('sort_order', 'DESC')
    completed_filter = request.args.get('filter', 'all')
    priority_filter = request.args.get('priority_filter', 'all')

    # Get search, sort, and filter clauses from helper functions
    search_clause, search_values = get_search_clause(search_query)
    sort_query = get_sort_clause(sort_by, sort_order)
    filter_clause = get_filter_clause(completed_filter, priority_filter)

        
    # Get tasks for the current page, excluding completed tasks from the main list
    offset = (page - 1) * tasks_per_page
    
    conn = sqlite3.connect('task-management.db')
    cursor = conn.cursor()
    
    # Fetch tasks based on filters, search, and sort, excluding completed tasks
    query = f"""
        SELECT Task_ID, TaskName, TaskDesc, Priority, Ranking, TaskDeadline, Completed 
        FROM tasks 
        WHERE User_ID = ? AND Completed = 'false' {search_clause} {filter_clause} {sort_query} 
        LIMIT ? OFFSET ?
    """
    parameters = (user_id, *search_values, tasks_per_page, offset)

    cursor.execute(query, parameters)
    tasks = cursor.fetchall()

    # Get completed tasks separately for the side panel
    cursor.execute(
        """SELECT Task_ID, TaskName, TaskDesc, Priority, Ranking, TaskDeadline, Completed 
           FROM tasks 
           WHERE User_ID = ? AND Completed = 'true'
        """, (user_id,)
    )
    completed_tasks = cursor.fetchall()

    # Calculate total number of tasks to determine number of pages
    cursor.execute("SELECT COUNT(*) FROM tasks WHERE User_ID = ? AND Completed = 'false'", (user_id,))
    total_tasks = cursor.fetchone()[0]
    total_pages = ceil(total_tasks / tasks_per_page) if total_tasks > 0 else 1

    # Close the connection to the database
    conn.close()
    
    # Render the dashboard with tasks, completed tasks, and pagination info
    return render_template(
        'dashboard.html', 
        name=user_name, 
        tasks=tasks,                 # Only incomplete tasks
        completed_tasks=completed_tasks,  # Only completed tasks for the panel
        page=page, 
        total_pages=total_pages, 
        search_query=search_query,
        sort_by=sort_by,
        sort_order=sort_order,
        completed_filter=completed_filter,
        priority_filter=priority_filter
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
        priority = request.form.get('Priority')
        ranking = request.form.get('ranking')
        deadline = request.form.get('deadline')
        print("Data from form: ")
        print(task_name, task_desc, priority, ranking, deadline)
        
        # Ensure all fields contain data
        if all([task_name, task_desc, priority, ranking, deadline]):
            try:
                # Execute the update query
                cursor.execute(
                    """UPDATE tasks SET TaskName = ?, TaskDesc = ?, Priority = ?, Ranking = ?, TaskDeadline = ? WHERE Task_ID = ? AND User_ID = ?""",
                    (task_name, task_desc, priority, ranking, deadline, task_id, user_id)
                )
                conn.commit()
                
                conn.close()
                # print(task_id)
                
                #Redirects back to the dashboard
                return redirect(url_for('dashboard'))
            
            except Exception as e:
                conn.rollback()
                # Pre-fetch the task to pass back to the template
                cursor.execute(
                    """SELECT TaskName, TaskDesc, Priority, Ranking, TaskDeadline 
                    FROM tasks WHERE Task_ID = ? AND User_ID = ?""",
                (task_id, user_id)
                )
                task = cursor.fetchone()
                return render_template('update_task.html', task=task, error=f"Error updating task: {e}")
            
        else:
            return render_template('update_task.html', task_id=task_id, error="All fields are required.")
    else:
        # Pre-fill the form with the existing task data
        cursor.execute(
            """SELECT TaskName, TaskDesc, Priority, Ranking, TaskDeadline 
               FROM tasks WHERE Task_ID = ? AND User_ID = ?""",
            (task_id, user_id)
        )
        task = cursor.fetchone()
        conn.close()
        
        if task:
            # print(task_id)
            return render_template('update_task.html', task=task)
        else:
            return redirect(url_for('dashboard'))


#This route handles the deletion of a task
@app.route('/delete_task', methods=['GET'])
def delete_task():
    #This retrives the task ID from query parameters
    task_id = request.args.get('task_id')
    #Retrieves the user ID from the session
    user_id = session.get('user_id')
    #This ensured that the user is logged in
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
        #In case the task is unable to be deleted for any reason
    except Exception as e:
        print(f"Error occurred: {e}")
        return render_template('dashboard.html', error="Failed to delete task.")
    finally:
        #Closes the connection to the server
        conn.close()
    #At the end of the process, the user is guided back to the dashboard
    return redirect(url_for('dashboard'))


#This is a helper function that will fetch the users tasks
def fetch_tasks(user_id):
    conn = sqlite3.connect('task-management.db')
    cursor = conn.cursor()
    cursor.execute(
        "SELECT Task_ID, TaskName, TaskDesc, Priority, Ranking, TaskDeadline "
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

#This is a helper function for the sorting functionality
def get_sort_clause(sort_by, sort_order): 
    valid_sort_columns = ['Priority', 'TaskName', 'TaskDeadline', 'DateTaskCreated', 'Ranking']

    # Ensure the primary sort column is valid
    if sort_by not in valid_sort_columns:
        sort_by = 'Priority'  # default sorting column

    # Start building the sort clause
    sort_clause = f"ORDER BY {sort_by} {sort_order}"

    # If the primary sort column is Priority, sort by Ranking as the secondary criterion
    if sort_by == 'Priority':
        sort_clause += ", Ranking " + sort_order  # Order for Ranking can be adjusted as needed

    return sort_clause



#This is a helper function for the filter functionality
def get_filter_clause(completed_filter, priority_filter):
    filter_clauses = []
    
    # Check if the filter is for completed or incomplete tasks
    if completed_filter == 'completed':
        filter_clauses.append("Completed = 'true'")
    elif completed_filter == 'incomplete':
        filter_clauses.append("Completed = 'false'")

    # Check if a priority filter is set
    if priority_filter and priority_filter != 'all':
        filter_clauses.append(f"Priority = '{priority_filter}'")

    # Combine all filter clauses with AND
    if filter_clauses:
        return "AND " + " AND ".join(filter_clauses)
    
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
    manage_cursor.execute("CREATE TABLE IF NOT EXISTS users(User_ID INTEGER PRIMARY KEY, Email text NOT NULL UNIQUE, Username text NOT NULL, Password text NOT NULL, DateAccountCreated text NOT NULL)")
    manage_cursor.execute("CREATE TABLE IF NOT EXISTS tasks(Task_ID INTEGER PRIMARY KEY, TaskName text NOT NULL, TaskDesc text NOT NULL, Priority Text NOT NULL, TaskDeadline text NOT NULL, DateTaskCreated text NOT NULL, Completed text NOT NULL, Ranking INTEGER, User_ID INTEGER NOT NULL, FOREIGN KEY(User_ID) REFERENCES users(User_ID))")

    #Then the changes are added to the database
    initial_connection.commit()

#End of Startup function


#This needs to be outside of the __name__ part, because Flask skips over it.
startup()
if __name__=='__main__':
    app.run()

#End of Script
