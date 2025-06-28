from datetime import datetime

from ext import db

from flask_login import UserMixin

 

class User(UserMixin, db.Model):

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100))

    email = db.Column(db.String(100), unique=True)

    password = db.Column(db.String(200))

   

    # Relația corect plasată în interiorul clasei

    signups = db.relationship('Signup', backref='user', lazy='dynamic')

 

class Project(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(200))

    description = db.Column(db.Text)

    date = db.Column(db.String(50))

    location = db.Column(db.String(100))

    max_volunteers = db.Column(db.Integer)

    image_filename = db.Column(db.String(200))

 

    # Relația cu înscrierile

    signups = db.relationship('Signup', backref='project', lazy='dynamic')

 

class Signup(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))

    timestamp = db.Column(db.DateTime, default=datetime.utcnow)