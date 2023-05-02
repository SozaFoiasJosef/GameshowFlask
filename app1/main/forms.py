from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, BooleanField, SelectField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

class QuestionForm(FlaskForm):
    answer = StringField('Answer', validators=[DataRequired()])
    submit = SubmitField('Submit')

class EditPointsForm(FlaskForm):
    points = SelectField('Points', choices=[('10', '10 points'), ('25', '25 points'), ('50', '50 points')])
    submit = SubmitField('Submit')

class EditTeamForm(FlaskForm):
    teams = SelectField('Points', choices=[('green', 'Green'), ('red', 'Red'), ('Blue', 'Blue')],
                         validators=[DataRequired()])
    submit = SubmitField('Submit')