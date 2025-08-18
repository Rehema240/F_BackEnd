from sqlalchemy.orm import Session
from uuid import UUID
from datetime import datetime

from event_api import models, schemas
from typing import Optional # Import Optional

# --- User CRUD ---
def get_user(db: Session, user_id: UUID):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

def create_user(db: Session, user: schemas.UserCreate, hashed_password: str):
    db_user = models.User(
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        hashed_password=hashed_password,
        role=user.role,
        department=user.department
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, db_user: models.User, user_update: schemas.UserCreate, hashed_password: Optional[str] = None):
    for key, value in user_update.dict(exclude_unset=True).items():
        if key == "password":
            db_user.hashed_password = hashed_password if hashed_password else db_user.hashed_password
        else:
            setattr(db_user, key, value)
    db.commit()
    db.refresh(db_user)
    return db_user

def delete_user(db: Session, user_id: UUID):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user:
        db.delete(db_user)
        db.commit()
    return db_user

# --- Event CRUD ---
def get_event(db: Session, event_id: UUID):
    return db.query(models.Event).filter(models.Event.id == event_id).first()

def get_events(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Event).offset(skip).limit(limit).all()

def create_event(db: Session, event: schemas.EventCreate, creator_id: UUID, creator_role: models.RoleEnum):
    db_event = models.Event(
        **event.dict(),
        creator_id=creator_id,
        creator_role=creator_role
    )
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    return db_event

def update_event(db: Session, db_event: models.Event, event_update: schemas.EventCreate):
    for key, value in event_update.dict(exclude_unset=True).items():
        setattr(db_event, key, value)
    db.commit()
    db.refresh(db_event)
    return db_event

def delete_event(db: Session, event_id: UUID):
    db_event = db.query(models.Event).filter(models.Event.id == event_id).first()
    if db_event:
        db.delete(db_event)
        db.commit()
    return db_event

# --- Opportunity CRUD ---
def get_opportunity(db: Session, opportunity_id: UUID):
    return db.query(models.Opportunity).filter(models.Opportunity.id == opportunity_id).first()

def get_opportunities(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Opportunity).offset(skip).limit(limit).all()

def create_opportunity(db: Session, opportunity: schemas.OpportunityCreate, posted_by_id: UUID, posted_by_role: models.RoleEnum):
    db_opportunity = models.Opportunity(
        **opportunity.dict(),
        posted_by_id=posted_by_id,
        posted_by_role=posted_by_role
    )
    db.add(db_opportunity)
    db.commit()
    db.refresh(db_opportunity)
    return db_opportunity

def update_opportunity(db: Session, db_opportunity: models.Opportunity, opportunity_update: schemas.OpportunityCreate):
    for key, value in opportunity_update.dict(exclude_unset=True).items():
        setattr(db_opportunity, key, value)
    db.commit()
    db.refresh(db_opportunity)
    return db_opportunity

def delete_opportunity(db: Session, opportunity_id: UUID):
    db_opportunity = db.query(models.Opportunity).filter(models.Opportunity.id == opportunity_id).first()
    if db_opportunity:
        db.delete(db_opportunity)
        db.commit()
    return db_opportunity

# --- EventConfirmation CRUD ---
def get_event_confirmation(db: Session, confirmation_id: UUID):
    return db.query(models.EventConfirmation).filter(models.EventConfirmation.id == confirmation_id).first()

def get_event_confirmations_for_event(db: Session, event_id: UUID):
    return db.query(models.EventConfirmation).filter(models.EventConfirmation.event_id == event_id).all()

def get_event_confirmations_for_student(db: Session, student_id: UUID):
    return db.query(models.EventConfirmation).filter(models.EventConfirmation.student_id == student_id).all()

def get_event_confirmation_by_student_and_event(db: Session, event_id: UUID, student_id: UUID):
    return db.query(models.EventConfirmation).filter(
        models.EventConfirmation.event_id == event_id,
        models.EventConfirmation.student_id == student_id
    ).first()

def create_event_confirmation(db: Session, confirmation: schemas.EventConfirmationCreate, student_id: UUID):
    # Explicitly extract fields to avoid potential dict parsing issues
    db_confirmation = models.EventConfirmation(
        event_id=confirmation.event_id,
        student_id=student_id,
        status=confirmation.status or models.ConfirmationStatusEnum.CONFIRMED,
        note=confirmation.note
    )
    db.add(db_confirmation)
    db.commit()
    db.refresh(db_confirmation)
    return db_confirmation

def delete_event_confirmation(db: Session, confirmation_id: UUID):
    db_confirmation = db.query(models.EventConfirmation).filter(models.EventConfirmation.id == confirmation_id).first()
    if db_confirmation:
        db.delete(db_confirmation)
        db.commit()
    return db_confirmation

# --- Notification CRUD ---
def get_notification(db: Session, notification_id: UUID):
    return db.query(models.Notification).filter(models.Notification.id == notification_id).first()

def get_notifications_for_recipient(db: Session, recipient_id: UUID, skip: int = 0, limit: int = 100):
    return db.query(models.Notification).filter(models.Notification.recipient_id == recipient_id).offset(skip).limit(limit).all()

def create_notification(db: Session, notification: schemas.NotificationCreate):
    db_notification = models.Notification(**notification.dict())
    db.add(db_notification)
    db.commit()
    db.refresh(db_notification)
    return db_notification

def update_notification(db: Session, db_notification: models.Notification, is_read: bool):
    db_notification.is_read = is_read
    db.commit()
    db.refresh(db_notification)
    return db_notification

def delete_notification(db: Session, notification_id: UUID):
    db_notification = db.query(models.Notification).filter(models.Notification.id == notification_id).first()
    if db_notification:
        db.delete(db_notification)
        db.commit()
    return db_notification

def send_event_notifications_to_students(db: Session, event_id: UUID, title: str, description: str):
    """
    Send notifications to all students when a new event is created
    """
    # Get the event
    event = get_event(db, event_id=event_id)
    if not event:
        return False
    
    # Get all student users
    student_users = db.query(models.User).filter(models.User.role == models.RoleEnum.STUDENT).all()
    
    # Create notifications for each student
    notifications = []
    for student in student_users:
        notification = models.Notification(
            recipient_id=student.id,
            title=f"New Event: {title}",
            body=description,
            type=models.NotificationTypeEnum.EVENT,
            related_event_id=event_id,
            is_read=False
        )
        db.add(notification)
        notifications.append(notification)
    
    db.commit()
    return notifications
