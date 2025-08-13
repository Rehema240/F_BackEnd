from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import uuid

from event_api.dependencies import SessionLocal, engine
from event_api.models import Base, User, Event, Opportunity, RoleEnum
from event_api.auth import get_password_hash

def create_initial_data(db: Session):
    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)

    # --- Create Users ---
    print("Creating initial users...")

    # Admin User
    admin_user = db.query(User).filter(User.email == "admin@example.com").first()
    if not admin_user:
        admin_user = User(
            username="adminuser",
            email="admin@example.com",
            full_name="Admin User",
            hashed_password=get_password_hash("adminpass"),
            role=RoleEnum.ADMIN,
            department="IT"
        )
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        print(f"Created Admin: {admin_user.email}")
    else:
        print(f"Admin user {admin_user.email} already exists.")

    # Head User
    head_user = db.query(User).filter(User.email == "head@example.com").first()
    if not head_user:
        head_user = User(
            username="headuser",
            email="head@example.com",
            full_name="Head of Department",
            hashed_password=get_password_hash("headpass"),
            role=RoleEnum.HEAD,
            department="Engineering"
        )
        db.add(head_user)
        db.commit()
        db.refresh(head_user)
        print(f"Created Head: {head_user.email}")
    else:
        print(f"Head user {head_user.email} already exists.")

    # Employee User
    employee_user = db.query(User).filter(User.email == "employee@example.com").first()
    if not employee_user:
        employee_user = User(
            username="employeeuser",
            email="employee@example.com",
            full_name="Regular Employee",
            hashed_password=get_password_hash("employeepass"),
            role=RoleEnum.EMPLOYEE,
            department="Engineering"
        )
        db.add(employee_user)
        db.commit()
        db.refresh(employee_user)
        print(f"Created Employee: {employee_user.email}")
    else:
        print(f"Employee user {employee_user.email} already exists.")

    # Student User
    student_user = db.query(User).filter(User.email == "student@example.com").first()
    if not student_user:
        student_user = User(
            username="studentuser",
            email="student@example.com",
            full_name="Enrolled Student",
            hashed_password=get_password_hash("studentpass"),
            role=RoleEnum.STUDENT,
            department="Computer Science"
        )
        db.add(student_user)
        db.commit()
        db.refresh(student_user)
        print(f"Created Student: {student_user.email}")
    else:
        print(f"Student user {student_user.email} already exists.")

    # --- Create Events ---
    print("\nCreating initial events...")

    # Admin created event (cannot be deleted by others)
    event1 = db.query(Event).filter(Event.title == "Admin-Led Tech Summit").first()
    if not event1:
        event1 = Event(
            title="Admin-Led Tech Summit",
            description="A major tech summit organized by the admin team.",
            location="Virtual",
            department="IT",
            start_time=datetime.utcnow() + timedelta(days=30),
            end_time=datetime.utcnow() + timedelta(days=31),
            capacity=1000,
            is_public=True,
            creator_id=admin_user.id,
            creator_role=admin_user.role
        )
        db.add(event1)
        db.commit()
        db.refresh(event1)
        print(f"Created Event: {event1.title}")
    else:
        print(f"Event '{event1.title}' already exists.")

    # Head created event
    event2 = db.query(Event).filter(Event.title == "Engineering Department Workshop").first()
    if not event2:
        event2 = Event(
            title="Engineering Department Workshop",
            description="Hands-on workshop for engineering students.",
            location="Building A, Room 101",
            department="Engineering",
            start_time=datetime.utcnow() + timedelta(days=45),
            end_time=datetime.utcnow() + timedelta(days=45, hours=4),
            capacity=50,
            is_public=False,
            creator_id=head_user.id,
            creator_role=head_user.role
        )
        db.add(event2)
        db.commit()
        db.refresh(event2)
        print(f"Created Event: {event2.title}")
    else:
        print(f"Event '{event2.title}' already exists.")

    # Employee created event
    event3 = db.query(Event).filter(Event.title == "Employee Wellness Session").first()
    if not event3:
        event3 = Event(
            title="Employee Wellness Session",
            description="A session focused on employee well-being.",
            location="Online",
            department="HR",
            start_time=datetime.utcnow() + timedelta(days=60),
            end_time=datetime.utcnow() + timedelta(days=60, hours=2),
            capacity=200,
            is_public=True,
            creator_id=employee_user.id,
            creator_role=employee_user.role
        )
        db.add(event3)
        db.commit()
        db.refresh(event3)
        print(f"Created Event: {event3.title}")
    else:
        print(f"Event '{event3.title}' already exists.")

    # --- Create Opportunities ---
    print("\nCreating initial opportunities...")

    opportunity1 = db.query(Opportunity).filter(Opportunity.title == "Software Engineering Internship").first()
    if not opportunity1:
        opportunity1 = Opportunity(
            title="Software Engineering Internship",
            description="Summer internship for aspiring software engineers.",
            link="http://example.com/internship",
            department="Engineering",
            posted_by_id=head_user.id,
            posted_by_role=head_user.role
        )
        db.add(opportunity1)
        db.commit()
        db.refresh(opportunity1)
        print(f"Created Opportunity: {opportunity1.title}")
    else:
        print(f"Opportunity '{opportunity1.title}' already exists.")

    opportunity2 = db.query(Opportunity).filter(Opportunity.title == "Data Science Scholarship").first()
    if not opportunity2:
        opportunity2 = Opportunity(
            title="Data Science Scholarship",
            description="Scholarship for students pursuing data science.",
            link="http://example.com/scholarship",
            department="Computer Science",
            posted_by_id=admin_user.id,
            posted_by_role=admin_user.role
        )
        db.add(opportunity2)
        db.commit()
        db.refresh(opportunity2)
        print(f"Created Opportunity: {opportunity2.title}")
    else:
        print(f"Opportunity '{opportunity2.title}' already exists.")

    db.close()
    print("\nInitial data creation complete.")

if __name__ == "__main__":
    db = SessionLocal()
    create_initial_data(db)
