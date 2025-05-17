from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField
from wtforms.validators import DataRequired

class SearchForm(FlaskForm):
    search_query = StringField('Search', validators=[DataRequired()])
    search_type = SelectField('Search In', choices=[
        ('user', 'Users'),
        ('subject', 'Subjects'),
        ('quiz', 'Quizzes')
    ])
    submit = SubmitField('Search')