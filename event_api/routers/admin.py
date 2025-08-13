from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from event_api.dependencies import get_db
from event_api.models import RoleEnum
from event_api.schemas import UserCreate, UserRead, EventCreate, EventRead, OpportunityCreate, OpportunityRead, EventConfirmationRead, NotificationCreate, NotificationRead, AdminDashboardData
from event_api.auth import get_current_admin_user, get_password_hash
from event_api import crud

router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
    dependencies=[Depends(get_current_admin_user)],
    responses={403: {"description": "Not authorized"}}
)

# Dashboard
@router.get("/dashboard", response_model=AdminDashboardData)
def get_admin_dashboard_data(db: Session = Depends(get_db)):
    total_users = db.query(crud.models.User).count()
    total_events = db.query(crud.models.Event).count()
    total_opportunities = db.query(crud.models.Opportunity).count()
    total_confirmations = db.query(crud.models.EventConfirmation).count()
    return AdminDashboardData(
        total_users=total_users,
        total_events=total_events,
        total_opportunities=total_opportunities,
        total_confirmations=total_confirmations
    )

# User Management
@router.post("/users/", response_model=UserRead)
def create_user_admin(user: UserCreate, db: Session = Depends(get_db)):
    db_user_username = crud.get_user_by_username(db, username=user.username)
    if db_user_username:
        raise HTTPException(status_code=400, detail="Username already registered")
    db_user_email = crud.get_user_by_email(db, email=user.email)
    if db_user_email:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = get_password_hash(user.password)
    return crud.create_user(db=db, user=user, hashed_password=hashed_password)

@router.get("/users/", response_model=List[UserRead])
def read_users_admin(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users

@router.get("/users/{user_id}", response_model=UserRead)
def read_user_admin(user_id: UUID, db: Session = Depends(get_db)):
    user = crud.get_user(db, user_id=user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/users/{user_id}", response_model=UserRead)
def update_user_admin(user_id: UUID, user_update: UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    hashed_password = get_password_hash(user_update.password) if user_update.password else None
    return crud.update_user(db=db, db_user=db_user, user_update=user_update, hashed_password=hashed_password)

@router.delete("/users/{user_id}")
def delete_user_admin(user_id: UUID, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    crud.delete_user(db, user_id=user_id)
    return {"message": "User deleted successfully"}

# Event Management
@router.post("/events/", response_model=EventRead)
def create_event_admin(event: EventCreate, db: Session = Depends(get_db), current_user: UserRead = Depends(get_current_admin_user)):
    return crud.create_event(db=db, event=event, creator_id=current_user.id, creator_role=current_user.role)

@router.put("/events/{event_id}", response_model=EventRead)
def update_event_admin(event_id: UUID, event_update: EventCreate, db: Session = Depends(get_db)):
    db_event = crud.get_event(db, event_id=event_id)
    if db_event is None:
        raise HTTPException(status_code=404, detail="Event not found")
    
    return crud.update_event(db=db, db_event=db_event, event_update=event_update)

@router.delete("/events/{event_id}")
def delete_event_admin(event_id: UUID, db: Session = Depends(get_db)):
    db_event = crud.get_event(db, event_id=event_id)
    if db_event is None:
        raise HTTPException(status_code=404, detail="Event not found")
    
    if db_event.creator_role == RoleEnum.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Events created by Admin cannot be deleted.")

    crud.delete_event(db, event_id=event_id)
    return {"message": "Event deleted successfully"}

# Opportunity Management
@router.post("/opportunities/", response_model=OpportunityRead)
def create_opportunity_admin(opportunity: OpportunityCreate, db: Session = Depends(get_db), current_user: UserRead = Depends(get_current_admin_user)):
    return crud.create_opportunity(db=db, opportunity=opportunity, posted_by_id=current_user.id, posted_by_role=current_user.role)

@router.put("/opportunities/{opportunity_id}", response_model=OpportunityRead)
def update_opportunity_admin(opportunity_id: UUID, opportunity_update: OpportunityCreate, db: Session = Depends(get_db)):
    db_opportunity = crud.get_opportunity(db, opportunity_id=opportunity_id)
    if db_opportunity is None:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    
    return crud.update_opportunity(db=db, db_opportunity=db_opportunity, opportunity_update=opportunity_update)

@router.delete("/opportunities/{opportunity_id}")
def delete_opportunity_admin(opportunity_id: UUID, db: Session = Depends(get_db)):
    db_opportunity = crud.get_opportunity(db, opportunity_id=opportunity_id)
    if db_opportunity is None:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    
    crud.delete_opportunity(db, opportunity_id=opportunity_id)
    return {"message": "Opportunity deleted successfully"}

# Event Confirmation
@router.get("/students_confirmed_for_any_event/", response_model=List[UserRead])
def get_students_confirmed_for_any_event_admin(db: Session = Depends(get_db)):
    confirmed_student_ids = db.query(crud.models.EventConfirmation.student_id).distinct().all()
    student_ids = [s_id for (s_id,) in confirmed_student_ids]
    students = db.query(crud.models.User).filter(crud.models.User.id.in_(student_ids)).all()
    return students

# Notification Management
@router.post("/notifications/", response_model=NotificationRead)
def create_notification_admin(notification: NotificationCreate, db: Session = Depends(get_db)):
    return crud.create_notification(db=db, notification=notification)

@router.delete("/notifications/{notification_id}")
def delete_notification_admin(notification_id: UUID, db: Session = Depends(get_db)):
    notification = crud.get_notification(db, notification_id=notification_id)
    if notification is None:
        raise HTTPException(status_code=404, detail="Notification not found")
    
    crud.delete_notification(db, notification_id=notification_id)
    return {"message": "Notification deleted successfully"}
