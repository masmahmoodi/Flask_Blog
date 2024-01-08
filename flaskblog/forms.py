from flask_wtf import FlaskForm
from flask_login import current_user
from flask_wtf.file import FileField , FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField,TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flaskblog.models import User


class RegistrationForm(FlaskForm):
    username = StringField("User Name",validators=[DataRequired(),Length(min=2,max=20)])
    email = StringField("Email",validators=[DataRequired(),Email()])
    password = PasswordField("Password",validators=[DataRequired()])
    confirm_password = PasswordField("Confirm Password",validators=[DataRequired(),EqualTo("password")])
    submit = SubmitField("Sign Up")
    def validate_username(self,username):
        if User.query.filter_by(username=username.data).first():
            raise ValidationError("That username is taken! choose different one")
    def validate_email(self,email):
        if User.query.filter_by(email=email.data).first():
            raise ValidationError("That email is taken! choose different one")
class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember = BooleanField("Remember Me")
    submit = SubmitField("Login")



class AccountUpdate(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    username = StringField("Username", validators=[DataRequired()])
    picture = FileField('Update your profile pic ',validators=[FileAllowed(['png','jpg'])])
    submit = SubmitField("Update")

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self,email):
        if email.data != current_user.email:
            if User.query.filter_by(email=email.data).first():
                raise ValidationError("That email is taken! choose different one")



class PostForm(FlaskForm):
    title = StringField('Title',validators=[DataRequired()])
    content = TextAreaField('Content', validators=[DataRequired()])
    submit = SubmitField('Post')

