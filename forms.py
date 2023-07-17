from wtforms import SelectField, StringField, PasswordField, SubmitField
from flask_wtf import FlaskForm
from wtforms.validators import DataRequired, Email, Length, Optional, EqualTo

class UserAddForm(FlaskForm):
    """Form to add users."""
    
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[Length(min=8)])

class UserEditForm(FlaskForm):
    """Form to edit users."""
    
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password (optional)', validators=[Length(min=8), Optional()])
    confirm_password = PasswordField('Confirm Password (if updating old password)', validators=[Length(min=8), Optional()])


class LoginForm(FlaskForm):
    """Form to login."""

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[Length(min=8)])




