from app import app, db
from models import Project

with app.app_context():
    projects = [
        Project(
            title="FII ȘI TU MOS CRĂCIUN!",
            description="Campanie de iarnă pentru copiii din medii defavorizate.",
            date="November - December | 2025",
            location="Online, CUGIR, TIMIȘOARA",
            max_volunteers=10
        ),
        Project(
            title="Campanie – Începe școala",
            description="Ajutăm cu rechizite copiii din mediul rural.",
            date="September | 2025",
            location="Online, CUGIR",
            max_volunteers=15
        ),
        Project(
            title="Campanie de sterilizare",
            description="Sprijinim sterilizarea animalelor fără stăpân.",
            date="Vineri, August 29 | 09:00 AM",
            location="CUGIR",
            max_volunteers=3
        )
    ]

    db.session.bulk_save_objects(projects)
    db.session.commit()
    print("✅ Proiectele au fost adăugate.")
