from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from .user import User
from wtforms import SubmitField, StringField
from wtforms.validators import DataRequired, Length, Email, ValidationError
from . import db_session


class UpdateAccountForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    name = StringField('Name',
                       validators=[Length(min=2, max=20)])
    surname = StringField('Surname',
                          validators=[Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])

    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png'])])

    submit = SubmitField('Update')

    def validate_username(self, username):
        if username.data != current_user.username:
            # user = User.query.filter_by(username=username.data).first()
            session = db_session.create_session()
            user = session.query(User).filter(username == username.data).first()
            if user:
                raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        if email.data != current_user.email:
            session = db_session.create_session()
            user = session.query(User).filter(email == email.data).first()
            if user:
                raise ValidationError('That email is taken. Please choose a different one.')
