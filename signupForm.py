# Creator: Israel Showell
# Start Date: 9/27/2024
# End Date: /2024
# Project: Prioitask - Task Management Application
# Version: 0.50

# Description:
"""
This is the signup form Python script in the task management web application!
This script creates the signup form that users use!
This web application allows users to create, log into, and manage an account, add tasks to their dashboard and run common functionalities on the tasks, and mark them complete!
The programming for this project was begun September 27th 2024 and was finished at ==!
"""

#These are the imported libaries I am using to make the program
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField,IntegerField,TextAreaField,SubmitField
from wtforms.validators import DataRequired

#Here, I create a form format that will be rendered by app.py and by the HTML page
class signUpForm(FlaskForm):
    #Creates the email field and requires users to use it.
    Email=StringField(label="Email",validators=[DataRequired()])
    #Creates the username field and requires users to use it.
    Username=StringField(label="Username",validators=[DataRequired()])
    #Creates the password field and requires users to use it.
    Password=PasswordField(label="Password",validators=[DataRequired()])
    #Creates the phone field and requires users to use it.
    PhoneNumber=IntegerField(label="Enter Mobile Number",validators=[DataRequired()])
    #Creates the Gender field 
    Gender=StringField(label="Gender")
    #Creates the address TextAreaField 
    Address=TextAreaField(label="Address")
    #Creates the username field and requires users to use it.
    Age=IntegerField(label="Age")
    #Creates the button for users to submit their form
    Submit=SubmitField(label="Send")

#End of Script
