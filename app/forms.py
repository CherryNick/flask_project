from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, PasswordField, BooleanField, \
    RadioField, FileField, TextAreaField
from wtforms.fields.html5 import DateField
from wtforms.validators import DataRequired, email, EqualTo, length, ValidationError, regexp, Length
from app.models import User


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember me')
    submit = SubmitField('Sign in')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=20)])
    email = StringField('email', validators=[email()])
    password = PasswordField('Password', validators=[DataRequired(),
                                                     EqualTo('confirm', message='Passwords must match')])
    confirm = PasswordField('Repeat password')
    submit = SubmitField('Sign up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data.title()).first()
        if user:
            raise ValidationError('Username already exists!')

    def validate_email(self, email):
        email = User.query.filter_by(email=email.data.lower()).first()
        if email:
            raise ValidationError('email already exists!')


class EditProfileForm(FlaskForm):
    gender = RadioField('gender', choices=['m', 'f'])
    media = FileField('Image File')
    info = TextAreaField('About me')
    date_of_birth = DateField('Date of birth')
    submit = SubmitField('Save')


class CreatePost(FlaskForm):
    text = TextAreaField('Text', validators=[Length(min=1, max=200)])
    media = FileField('Image File')
    submit = SubmitField('Submit')



