from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, DateField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from models.user import User

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[
        DataRequired(),
        Email()
    ])
    password = PasswordField('Password', validators=[
        DataRequired()
    ])
    submit = SubmitField('Login')


class RegisterForm(FlaskForm):
    email = StringField('Email', validators=[
        DataRequired(),
        Email()
    ])
    full_name = StringField('Full Name', validators=[
        DataRequired(),
        Length(min=3, max=100)
    ])
    qualification = StringField('Qualification')
    dob = DateField('Date of Birth', format='%Y-%m-%d')
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=6)
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match.')
    ])
    submit = SubmitField('Register')
    
    def validate_email(self, email):
        user = User.query.filter_by(username=email.data).first()
        if user:
            raise ValidationError('That email is already registered. Please choose a different one.')