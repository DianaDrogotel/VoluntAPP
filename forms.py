from flask_wtf import FlaskForm

from wtforms import StringField, PasswordField, SubmitField, TextAreaField, DateField, IntegerField

from wtforms.validators import DataRequired, Email, EqualTo

from flask_wtf.file import FileField, FileAllowed

 

class RegisterForm(FlaskForm):

    name = StringField('Nume', validators=[DataRequired()])

    email = StringField('Email', validators=[DataRequired(), Email()])

    password = PasswordField('Parolă', validators=[DataRequired()])

    confirm_password = PasswordField('Confirmă parola', validators=[DataRequired(), EqualTo('password', message='Parolele trebuie să fie identice.')])

    submit = SubmitField('Înregistrare')

 

class LoginForm(FlaskForm):

    email = StringField('Email', validators=[DataRequired(), Email()])

    password = PasswordField('Parolă', validators=[DataRequired()])

    submit = SubmitField('Autentificare')

 

class ProjectForm(FlaskForm):

    title = StringField('Titlu', validators=[DataRequired()])

    description = TextAreaField('Descriere', validators=[DataRequired()])

    date = DateField('Data', validators=[DataRequired()])

    location = StringField('Locație', validators=[DataRequired()])

    max_volunteers = IntegerField('Număr maxim de voluntari', validators=[DataRequired()])

    image = FileField('Imagine proiect', validators=[FileAllowed(['jpg', 'jpeg', 'png'], 'Doar imagini (.jpg, .png) sunt permise.')])


    submit = SubmitField('Adaugă proiect')