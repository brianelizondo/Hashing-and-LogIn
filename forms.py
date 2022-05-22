""" Forms for for Feedback app """
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, EmailField
from wtforms.validators import InputRequired

class AddUserForm(FlaskForm):
    """ Form for adding Users """

    username = StringField("Username", validators=[InputRequired(message='Please enter your Username')])
    password = PasswordField("Password", validators=[InputRequired(message='Please enter your Password')])
    email = EmailField("E-mail", validators=[InputRequired(message='Please enter your Email')])
    first_name = StringField("First Name", validators=[InputRequired(message='Please enter your First Name')])
    last_name = StringField("Last Name", validators=[InputRequired(message='Please enter your Last Name')])


class LoginForm(FlaskForm):
    """ Form for login Users """

    username = StringField("Username", validators=[InputRequired(message='Please enter your Username')])
    password = PasswordField("Password", validators=[InputRequired(message='Please enter your Password')])