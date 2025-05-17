from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, IntegerField, SelectField, BooleanField, PasswordField, FloatField, SubmitField
from wtforms.validators import DataRequired, Length, Email, NumberRange, Optional, EqualTo

class SubjectForm(FlaskForm):
    """Form for creating and editing subjects."""
    name = StringField('Subject Name', validators=[
        DataRequired(),
        Length(min=2, max=100)
    ])
    description = TextAreaField('Description', validators=[
        Optional(),
        Length(max=500)
    ])
    submit = SubmitField('Submit')

class ChapterForm(FlaskForm):
    """Form for creating and editing chapters."""
    name = StringField('Chapter Name', validators=[
        DataRequired(),
        Length(min=2, max=100)
    ])
    description = TextAreaField('Description', validators=[
        Optional(),
        Length(max=500)
    ])
    subject_id = SelectField('Subject', coerce=int, validators=[
        DataRequired()
    ])
    submit = SubmitField('Submit')

class QuizForm(FlaskForm):
    """Form for creating and editing quizzes."""
    title = StringField('Quiz Title', validators=[
        DataRequired(),
        Length(min=3, max=200)
    ])
    description = TextAreaField('Description', validators=[
        Optional(),
        Length(max=1000)
    ])
    time_limit = IntegerField('Time Limit (minutes)', validators=[
        DataRequired(),
        NumberRange(min=1, max=180)
    ])
    chapter_id = SelectField('Chapter', coerce=int, validators=[
        DataRequired()
    ])
    is_active = BooleanField('Active', default=True)
    submit = SubmitField('Submit')

class QuestionForm(FlaskForm):
    """Form for creating and editing quiz questions."""
    question_text = TextAreaField('Question', validators=[
        DataRequired(),
        Length(min=5, max=1000)
    ])
    option1 = StringField('Option 1', validators=[
        DataRequired(),
        Length(max=255)
    ])
    option2 = StringField('Option 2', validators=[
        DataRequired(),
        Length(max=255)
    ])
    option3 = StringField('Option 3', validators=[
        DataRequired(),
        Length(max=255)
    ])
    option4 = StringField('Option 4', validators=[
        DataRequired(),
        Length(max=255)
    ])
    correct_answer = SelectField('Correct Answer', 
                                choices=[('1', 'Option 1'), 
                                         ('2', 'Option 2'), 
                                         ('3', 'Option 3'), 
                                         ('4', 'Option 4')], 
                                validators=[DataRequired()])
    mark = FloatField('Marks', validators=[
        DataRequired(),
        NumberRange(min=0.5, max=10)
    ], default=1)
    submit = SubmitField('Submit')

class UserForm(FlaskForm):
    """Form for editing user accounts."""
    username = StringField('Email', validators=[
        DataRequired(),
        Email(),
        Length(max=100)
    ])
    full_name = StringField('Full Name', validators=[
        DataRequired(),
        Length(min=3, max=100)
    ])
    qualification = StringField('Qualification', validators=[
        Optional(),
        Length(max=100)
    ])
    password = PasswordField('New Password', validators=[
        Optional(),
        Length(min=6)
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        EqualTo('password', message='Passwords must match.')
    ])
    is_admin = BooleanField('Admin Access', default=False)
    submit = SubmitField('Submit')