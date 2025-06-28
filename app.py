from flask import Flask, render_template, redirect, url_for, flash, request

from flask_login import login_user, login_required, logout_user, current_user

from werkzeug.security import generate_password_hash, check_password_hash

from werkzeug.utils import secure_filename

from datetime import datetime

import os

import pandas as pd

import xlsxwriter

import smtplib

from email.mime.text import MIMEText

from email.mime.multipart import MIMEMultipart

from ext import db, login_manager

from models import User, Project, Signup

from forms import RegisterForm, LoginForm, ProjectForm

 

app = Flask(__name__)

app.config['SECRET_KEY'] = 'ceva-secret'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

app.config['UPLOAD_FOLDER'] = 'static/uploads'

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

 

db.init_app(app)

login_manager.init_app(app)

login_manager.login_view = 'login'

 

@login_manager.user_loader

def load_user(user_id):

    return User.query.get(int(user_id))

 

@app.route('/')

def index():

    return redirect(url_for('projects'))

 

@app.route('/register', methods=['GET', 'POST'])

def register():

    form = RegisterForm()

    if form.validate_on_submit():

        existing_user = User.query.filter_by(email=form.email.data).first()

        if existing_user:

            flash('Există deja un cont cu acest email.', 'danger')

            return redirect(url_for('register'))

        hashed_password = generate_password_hash(form.password.data)

        new_user = User(name=form.name.data, email=form.email.data, password=hashed_password)

        db.session.add(new_user)

        db.session.commit()

        login_user(new_user)

        flash('Cont creat cu succes!', 'success')

        return redirect(url_for('projects'))

    return render_template('register.html', form=form)

 

@app.route('/login', methods=['GET', 'POST'])

def login():

    form = LoginForm()

    if form.validate_on_submit():

        user = User.query.filter_by(email=form.email.data).first()

        if user and check_password_hash(user.password, form.password.data):

            login_user(user)

            flash("Autentificat cu succes!", "success")

            return redirect(url_for('projects'))

        else:

            flash("Email sau parolă incorecte.", "danger")

    return render_template('login.html', form=form)

 

@app.route('/logout', methods=['POST'])

@login_required

def logout():

    logout_user()

    flash("Te-ai delogat cu succes!")

    return redirect(url_for('login'))

 

@app.route('/projects')

@login_required

def projects():

    all_projects = Project.query.all()

    for project in all_projects:

        project.signup_count = project.signups.count()

        try:

            project.date_converted = datetime.strptime(project.date, "%Y-%m-%d")

        except ValueError:

            project.date_converted = datetime.max

    signed_up_project_ids = [signup.project_id for signup in current_user.signups]

    current_date = datetime.now()

    return render_template('projects.html', projects=all_projects, signed_up_project_ids=signed_up_project_ids, current_date=current_date)

 

@app.route('/add_project', methods=['GET', 'POST'])

@login_required

def add_project():

    if current_user.email != 'admin@dspus.ro':

        flash('Nu ai acces la această pagină.', 'danger')

        return redirect(url_for('projects'))

    form = ProjectForm()

    if form.validate_on_submit():

        filename = None

        if form.image.data:

            image = form.image.data

            filename = secure_filename(image.filename)

            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        new_project = Project(title=form.title.data, description=form.description.data, date=form.date.data,

                              location=form.location.data, max_volunteers=form.max_volunteers.data, image_filename=filename)

        db.session.add(new_project)

        db.session.commit()

        flash('Proiectul a fost adăugat cu succes!', 'success')

        return redirect(url_for('projects'))

    return render_template('add_project.html', user=current_user, form=form)

 

@app.route('/signup/<int:project_id>', methods=['POST'])

@login_required

def signup(project_id):

    project = Project.query.get_or_404(project_id)

    existing = Signup.query.filter_by(user_id=current_user.id, project_id=project_id).first()

    if not existing and project.signups.count() < project.max_volunteers:

        signup = Signup(user_id=current_user.id, project_id=project_id)

        db.session.add(signup)

        db.session.commit()

    return redirect(url_for('projects'))

 

@app.route('/cancel_signup/<int:project_id>', methods=['POST'])

@login_required

def cancel_signup(project_id):

    signup = Signup.query.filter_by(user_id=current_user.id, project_id=project_id).first()

    if signup:

        db.session.delete(signup)

        db.session.commit()

    return redirect(url_for('projects'))

 

@app.route('/delete_project/<int:project_id>', methods=['POST'])

@login_required

def delete_project(project_id):

    if current_user.email != 'admin@dspus.ro':

        flash('Nu ai permisiunea să ștergi proiecte.', 'danger')

        return redirect(url_for('projects'))

    project = Project.query.get_or_404(project_id)

    Signup.query.filter_by(project_id=project_id).delete()

    db.session.delete(project)

    db.session.commit()

    flash('Proiectul a fost șters cu succes.', 'success')

    return redirect(url_for('projects'))

 

@app.route('/get_volunteers/<int:project_id>')

@login_required

def get_volunteers(project_id):

    project = Project.query.get_or_404(project_id)

    volunteers = [{'name': s.user.name, 'email': s.user.email} for s in project.signups]

    return {'volunteers': volunteers}

 

@app.route('/remove_volunteer/<int:project_id>/<string:email>', methods=['POST'])

@login_required

def remove_volunteer(project_id, email):

    user = User.query.filter_by(email=email).first()

    if user:

        signup = Signup.query.filter_by(user_id=user.id, project_id=project_id).first()

        if signup:

            db.session.delete(signup)

            db.session.commit()

    return redirect(url_for('projects'))

 

@app.route('/export_volunteers/<int:project_id>')

@login_required

def export_volunteers(project_id):

    project = Project.query.get_or_404(project_id)

    volunteers = [{'Nume': s.user.name, 'Email': s.user.email} for s in project.signups]

    df = pd.DataFrame(volunteers)

    output_path = os.path.join("static", f"voluntari_proiect_{project_id}.xlsx")

    df.to_excel(output_path, index=False, engine='xlsxwriter')

    return redirect('/' + output_path)

 

@app.route('/manage_volunteers')

@login_required

def manage_volunteers():

    if current_user.email != 'admin@dspus.ro':

        flash("Acces restricționat!", 'danger')

        return redirect(url_for('projects'))

    users = User.query.all()

    return render_template('manage_volunteers.html', users=users)

 

@app.route('/send_email', methods=['POST'])

@login_required

def send_email():

    if current_user.email != 'admin@dspus.ro':

        flash("Acces nepermis.", 'danger')

        return redirect(url_for('projects'))

 

    subject = request.form.get('subject')

    message = request.form.get('message')

    recipients = request.form.getlist('recipients')

 

    sender_email = "dianadrogotel25@gmail.com"

    sender_password = "zmfu bmvw eafp zwax"

 

    for recipient in recipients:

        msg = MIMEMultipart()

        msg['From'] = sender_email

        msg['To'] = recipient

        msg['Subject'] = subject

        msg.attach(MIMEText(message, 'plain'))

 

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:

            server.login(sender_email, sender_password)

            server.send_message(msg)

 

    flash("Email-uri trimise cu succes!", 'success')

    return redirect(url_for('manage_volunteers'))

 

@app.route('/my_projects')

@login_required

def my_projects():

    projects = Project.query.join(Signup).filter(Signup.user_id == current_user.id).all()

    signed_up_project_ids = [signup.project_id for signup in Signup.query.filter_by(user_id=current_user.id).all()]

    return render_template('my_projects.html', projects=projects, signed_up_project_ids=signed_up_project_ids)

 

if __name__ == '__main__':

    with app.app_context():

        db.create_all()

    app.run(debug=True)