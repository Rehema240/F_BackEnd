from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from event_api.dependencies import get_db
from event_api.models import RoleEnum
from event_api.schemas import UserCreate, UserRead, EventRead, OpportunityRead, EventConfirmationCreate, EventConfirmationRead, NotificationRead
from event_api.auth import get_current_student_user, get_current_user, get_password_hash
from event_api import crud

router = APIRouter(
    prefix="/student",
    tags=["Student"],
    dependencies=[Depends(get_current_student_user)],
    responses={403: {"description": "Not authorized"}}
)

# Dashboard Endpoints (example)
# Dashboard Endpoints (example)
@router.get("/dashboard/my_confirmations/", response_model=List[EventConfirmationRead])
def get_my_confirmations(db: Session = Depends(get_db), current_user: UserRead = Depends(get_current_student_user)):
    confirmations = db.query(crud.models.EventConfirmation).filter(crud.models.EventConfirmation.student_id == current_user.id).all()
    return confirmations

# Profile Settings Management
# Profile Settings Management
@router.get("/me/", response_model=UserRead)
def read_users_me_student(current_user: UserRead = Depends(get_current_student_user)):
    return current_user

@router.put("/me/", response_model=UserRead)
def update_users_me_student(user_update: UserCreate, db: Session = Depends(get_db), current_user: UserRead = Depends(get_current_student_user)):
    db_user = crud.get_user(db, user_id=current_user.id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    hashed_password = get_password_hash(user_update.password) if user_update.password else None
    return crud.update_user(db=db, db_user=db_user, user_update=user_update, hashed_password=hashed_password)

# Event Browsing (Read-only)
# Event Browsing (Read-only)
@router.get("/events/", response_model=List[EventRead])
def read_events_student(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    events = db.query(crud.models.Event).filter(crud.models.Event.is_public == True).offset(skip).limit(limit).all()
    return events

@router.get("/events/{event_id}", response_model=EventRead)
def read_event_student(event_id: UUID, db: Session = Depends(get_db), current_user: UserRead = Depends(get_current_student_user)):
    event = crud.get_event(db, event_id=event_id)
    if event is None:
        raise HTTPException(status_code=404, detail="Event not found")
    
    # Students can view public events or events they are confirmed for
    is_confirmed = crud.get_event_confirmation_by_student_and_event(db, event_id=event_id, student_id=current_user.id)
    
    if not event.is_public and not is_confirmed:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view this event.")
    
    return event

@router.get("/events/calendar_view/", response_model=List[EventRead])
def get_events_for_calendar_student(
    start_time: datetime,
    end_time: datetime,
    db: Session = Depends(get_db),
    current_user: UserRead = Depends(get_current_student_user)
):
    confirmed_event_ids = db.query(crud.models.EventConfirmation.event_id).filter(
        crud.models.EventConfirmation.student_id == current_user.id
    ).subquery()
    
    query = db.query(crud.models.Event).filter(
        crud.models.Event.start_time >= start_time,
        crud.models.Event.start_time <= end_time,
        (crud.models.Event.is_public == True) | (crud.models.Event.id.in_(confirmed_event_ids))
    )
    events = query.all()
    return events

# Opportunity Browsing (Read-only)
@router.get("/opportunities/", response_model=List[OpportunityRead])
def read_opportunities_student(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    opportunities = crud.get_opportunities(db, skip=skip, limit=limit)
    return opportunities

@router.get("/opportunities/{opportunity_id}", response_model=OpportunityRead)
def read_opportunity_student(opportunity_id: UUID, db: Session = Depends(get_db)):
    opportunity = crud.get_opportunity(db, opportunity_id=opportunity_id)
    if opportunity is None:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    return opportunity

# Event Confirmation
@router.post("/event_confirmations/", response_model=EventConfirmationRead)
def create_event_confirmation_student(confirmation: EventConfirmationCreate, db: Session = Depends(get_db), current_user: UserRead = Depends(get_current_student_user)):
    # Validate event exists
    event = crud.get_event(db, event_id=confirmation.event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    # Check if student already confirmed
    existing_confirmation = crud.get_event_confirmation_by_student_and_event(db, event_id=confirmation.event_id, student_id=current_user.id)
    if existing_confirmation:
        raise HTTPException(status_code=400, detail="Student already confirmed for this event")

    # Set default status if not provided
    if confirmation.status is None:
        confirmation.status = crud.models.ConfirmationStatusEnum.CONFIRMED
        
    try:
        # Create confirmation
        db_confirmation = crud.create_event_confirmation(db=db, confirmation=confirmation, student_id=current_user.id)
        
        # Increment confirmation count
        event.confirmation_count += 1
        db.commit()
        db.refresh(event)
        
        return db_confirmation
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=422, detail=f"Error creating confirmation: {str(e)}")

@router.get("/my_event_confirmations/", response_model=List[EventConfirmationRead])
def get_my_event_confirmations_student(db: Session = Depends(get_db), current_user: UserRead = Depends(get_current_student_user)):
    confirmations = crud.get_event_confirmations_for_student(db, student_id=current_user.id)
    return confirmations

@router.get("/event_confirmations/debug/{event_id}")
def debug_event_confirmation(event_id: UUID, db: Session = Depends(get_db), current_user: UserRead = Depends(get_current_student_user)):
    """Debug endpoint to check event confirmation data structure"""
    # Get the event
    event = crud.get_event(db, event_id=event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
        
    # Create a sample confirmation data structure
    sample_data = {
        "event_id": str(event_id),
        "note": "Optional note from student",
        "status": "confirmed"
    }
    
    return {
        "message": "Use this format for creating event confirmations",
        "sample_data": sample_data
    }

# Notification Endpoints
@router.get("/notifications/", response_model=List[NotificationRead])
def read_notifications_student(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: UserRead = Depends(get_current_student_user)):
    notifications = crud.get_notifications_for_recipient(db, recipient_id=current_user.id, skip=skip, limit=limit)
    return notifications

@router.get("/notifications/{notification_id}", response_model=NotificationRead)
def read_notification_student(notification_id: UUID, db: Session = Depends(get_db), current_user: UserRead = Depends(get_current_student_user)):
    notification = crud.get_notification(db, notification_id=notification_id)
    if notification is None:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    if notification.recipient_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view this notification")
    
    return notification

@router.put("/notifications/{notification_id}/read", response_model=NotificationRead)
def mark_notification_as_read_student(notification_id: UUID, db: Session = Depends(get_db), current_user: UserRead = Depends(get_current_student_user)):
    notification = crud.get_notification(db, notification_id=notification_id)
    if notification is None:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    if notification.recipient_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to mark this notification as read")
    
    return crud.update_notification(db, db_notification=notification, is_read=True)
