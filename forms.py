from flask_wtf import FlaskForm
from wtforms import DateField
from wtforms.validators import InputRequired, DataRequired

class DateForm(FlaskForm):
    date = DateField("Game Date", validators = [DataRequired()])

