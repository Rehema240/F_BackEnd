from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from event_api.dependencies import get_db
from event_api.models import RoleEnum
from event_api.schemas import UserCreate, UserRead, EventCreate, EventRead, OpportunityRead, EventConfirmationRead, NotificationRead
from event_api.auth import get_current_employee_user, get_current_user, get_password_hash
from event_api import crud

router = APIRouter(
    prefix="/employee",
    tags=["Employee"],
    dependencies=[Depends(get_current_employee_user)],
    responses={403: {"description": "Not authorized"}}
)

# Dashboard Endpoints (example)
# Dashboard Endpoints (example)
@router.get("/dashboard/my_events/", response_model=List[EventRead])
def get_my_events(db: Session = Depends(get_db), current_user: UserRead = Depends(get_current_employee_user)):
    events = db.query(crud.models.Event).filter(crud.models.Event.creator_id == current_user.id).all()
    return events

# Profile Settings Management
# Profile Settings Management
@router.get("/me/", response_model=UserRead)
def read_users_me_employee(current_user: UserRead = Depends(get_current_employee_user)):
    return current_user

@router.put("/me/", response_model=UserRead)
def update_users_me_employee(user_update: UserCreate, db: Session = Depends(get_db), current_user: UserRead = Depends(get_current_employee_user)):
    db_user = crud.get_user(db, user_id=current_user.id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    hashed_password = get_password_hash(user_update.password) if user_update.password else None
    return crud.update_user(db=db, db_user=db_user, user_update=user_update, hashed_password=hashed_password)

# Event Management
@router.post("/events/", response_model=EventRead)
def create_event_employee(event: EventCreate, db: Session = Depends(get_db), current_user: UserRead = Depends(get_current_employee_user)):
    new_event = crud.create_event(db=db, event=event, creator_id=current_user.id, creator_role=current_user.role)
    
    # Send notifications to all students about the new event
    department_info = f" in the {new_event.department} department" if new_event.department else ""
    crud.send_event_notifications_to_students(
        db=db, 
        event_id=new_event.id,
        title=new_event.title,
        description=new_event.description if new_event.description else f"A new event has been created by an employee{department_info}."
    )
    
    return new_event

@router.get("/events/", response_model=List[EventRead])
def read_events_employee(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: UserRead = Depends(get_current_employee_user)):
    events = db.query(crud.models.Event).filter(crud.models.Event.creator_id == current_user.id).offset(skip).limit(limit).all()
    return events

@router.get("/events/{event_id}", response_model=EventRead)
def read_event_employee(event_id: UUID, db: Session = Depends(get_db), current_user: UserRead = Depends(get_current_employee_user)):
    event = crud.get_event(db, event_id=event_id)
    if event is None:
        raise HTTPException(status_code=404, detail="Event not found")
    if event.creator_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view this event.")
    return event

@router.put("/events/{event_id}", response_model=EventRead)
def update_event_employee(event_id: UUID, event_update: EventCreate, db: Session = Depends(get_db), current_user: UserRead = Depends(get_current_employee_user)):
    db_event = crud.get_event(db, event_id=event_id)
    if db_event is None:
        raise HTTPException(status_code=404, detail="Event not found")
    
    if db_event.creator_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Employees can only update their own events.")

    return crud.update_event(db=db, db_event=db_event, event_update=event_update)

@router.delete("/events/{event_id}")
def delete_event_employee(event_id: UUID, db: Session = Depends(get_db), current_user: UserRead = Depends(get_current_employee_user)):
    db_event = crud.get_event(db, event_id=event_id)
    if db_event is None:
        raise HTTPException(status_code=404, detail="Event not found")
    
    if db_event.creator_role == RoleEnum.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Events created by Admin cannot be deleted.")
    if db_event.creator_role == RoleEnum.HEAD:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Events created by Head cannot be deleted by Employee.")
    if db_event.creator_id != current_user.id or db_event.creator_role != RoleEnum.EMPLOYEE:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Employees can only delete events created by Employee role.")

    crud.delete_event(db, event_id=event_id)
    return {"message": "Event deleted successfully"}

@router.get("/events/calendar_view/", response_model=List[EventRead])
def get_events_for_calendar_employee(
    start_time: datetime,
    end_time: datetime,
    db: Session = Depends(get_db),
    current_user: UserRead = Depends(get_current_employee_user)
):
    query = db.query(crud.models.Event).filter(
        crud.models.Event.start_time >= start_time,
        crud.models.Event.start_time <= end_time,
        crud.models.Event.creator_id == current_user.id
    )
    events = query.all()
    return events

# Opportunity Read-only
@router.get("/opportunities/", response_model=List[OpportunityRead])
def read_opportunities_employee(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    opportunities = crud.get_opportunities(db, skip=skip, limit=limit)
    return opportunities

@router.get("/opportunities/{opportunity_id}", response_model=OpportunityRead)
def read_opportunity_employee(opportunity_id: UUID, db: Session = Depends(get_db)):
    opportunity = crud.get_opportunity(db, opportunity_id=opportunity_id)
    if opportunity is None:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    return opportunity

# Event Confirmation
@router.get("/events/{event_id}/confirmations", response_model=List[EventConfirmationRead])
def get_event_confirmations_employee(event_id: UUID, db: Session = Depends(get_db), current_user: UserRead = Depends(get_current_employee_user)):
    event = crud.get_event(db, event_id=event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    if event.creator_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view confirmations for this event.")

    confirmations = crud.get_event_confirmations_for_event(db, event_id=event_id)
    return confirmations

# Notification Endpoints
@router.get("/notifications/", response_model=List[NotificationRead])
def read_notifications_employee(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: UserRead = Depends(get_current_employee_user)):
    notifications = crud.get_notifications_for_recipient(db, recipient_id=current_user.id, skip=skip, limit=limit)
    return notifications

@router.get("/notifications/{notification_id}", response_model=NotificationRead)
def read_notification_employee(notification_id: UUID, db: Session = Depends(get_db), current_user: UserRead = Depends(get_current_employee_user)):
    notification = crud.get_notification(db, notification_id=notification_id)
    if notification is None:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    if notification.recipient_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view this notification")
    
    return notification

@router.put("/notifications/{notification_id}/read", response_model=NotificationRead)
def mark_notification_as_read_employee(notification_id: UUID, db: Session = Depends(get_db), current_user: UserRead = Depends(get_current_employee_user)):
    notification = crud.get_notification(db, notification_id=notification_id)
    if notification is None:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    if notification.recipient_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to mark this notification as read")
    
    return crud.update_notification(db, db_notification=notification, is_read=True)
