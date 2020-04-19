from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField


class SearchByUsernameForm(FlaskForm):
    username = StringField('Search by Username')
    submit = SubmitField('Submit')


class SearchByTitleForm(FlaskForm):
    title = StringField('Search by Title')
    submit = SubmitField('Submit')
