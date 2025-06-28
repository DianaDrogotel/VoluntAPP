from app import app

from ext import db

from models import User

from werkzeug.security import generate_password_hash

 

with app.app_context():

    db.drop_all()

    db.create_all()

 

    # Creează utilizatorul admin

    admin_email = "admin@dspus.ro"

    existing = User.query.filter_by(email=admin_email).first()

    if not existing:

        admin = User(

            name="Admin",

            email=admin_email,

            password=generate_password_hash("admin123")

        )

        db.session.add(admin)

        db.session.commit()

        print("✅ Utilizatorul admin a fost creat.")

    else:

        print("ℹ️ Utilizatorul admin există deja.")

   

    # Afișăm ce utilizatori avem

    users = User.query.all()

    print("👥 Utilizatori în baza de date:")

    for user in users:

        print(f" - {user.name} ({user.email})")