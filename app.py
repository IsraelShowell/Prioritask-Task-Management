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

#These are the imported libaries we are using to make the program
from datetime import datetime
import sqlite3
import random



#This is the start up function that runs when the app is ran in the command line to start
def startup():
    #Connects to the database
    initial_connection = sqlite3.connect('task-management.db')
    #Sets a cursor to each database
    manage_cursor =  initial_connection.cursor()
    #Runs a query to create a table if it does not exist
    #The data parameters that the tables can handle are a text username and a text password, etc
    #PRIMARY KEY automatically adds the UNIQUE constraint!
    manage_cursor.execute("CREATE TABLE IF NOT EXISTS users(User_ID INTEGER PRIMARY KEY, Username text NOT NULL, Password text NOT NULL, PhoneNumber INTEGER NOT NULL, Gender text NOT NULL, Address text NOT NULL, Age INTEGER NOT NULL, DateAccountCreated text NOT NULL)")
    manage_cursor.execute("CREATE TABLE IF NOT EXISTS tasks(Task_ID INTEGER PRIMARY KEY, TaskName text NOT NULL, TaskDesc text NOT NULL, Importance INTEGER NOT NULL, Urgency INTEGER NOT NULL, TaskDeadline text NOT NULL, DateTaskCreated text NOT NULL, User_ID INTEGER NOT NULL, Username text NOT NULL, FOREIGN KEY(User_ID) REFERENCES users(User_ID), FOREIGN KEY(Username) REFERENCES users(Username))")

    #Then the changes are added to the database
    initial_connection.commit()

#End of Startup function















#This is the function call
startup()


#End of Script
