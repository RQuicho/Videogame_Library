from wtforms import SelectField, StringField
from flask_wtf import FlaskForm
from wtforms.validators import InputRequired

class UserAddForm(FlaskForm):
    """Form to add users."""
    