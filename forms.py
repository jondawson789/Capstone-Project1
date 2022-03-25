from flask_wtf import FlaskForm
from wtforms import DateField, PasswordField, StringField
from wtforms.validators import InputRequired, DataRequired, Length, Email

class DateForm(FlaskForm):
    date = DateField("Game Date", validators = [DataRequired()])

class LoginForm(FlaskForm):
    username = StringField("Username", validators = [InputRequired(),
    Length(min=1, max=20)])

    password = PasswordField("Password", validators = [InputRequired()])

class RegisterForm(FlaskForm):
    username = StringField("Username", validators = [InputRequired(),
    Length(min=1, max=20)])

    password = PasswordField("Password", validators = [InputRequired()])

    email = StringField("Email", validators = [InputRequired(), Email(), Length(max=50)])

    first_name = StringField("First Name", validators = [InputRequired(), Length(max=30)])

    last_name = StringField("Last Name", validators = [InputRequired(), Length(max=30)])
