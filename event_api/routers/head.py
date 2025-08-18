from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from datetime import datetime

from event_api.dependencies import get_db
from event_api.models import RoleEnum
from event_api.schemas import UserRead, EventCreate, EventRead, OpportunityCreate, OpportunityRead, EventConfirmationRead, HeadDashboardData
from event_api.auth import get_current_head_user
from event_api import crud

router = APIRouter(
    prefix="/head",
    tags=["Head"],
    dependencies=[Depends(get_current_head_user)],
    responses={403: {"description": "Not authorized"}}
)

# Dashboard
@router.get("/dashboard", response_model=HeadDashboardData)
def get_head_dashboard_data(db: Session = Depends(get_db), current_user: UserRead = Depends(get_current_head_user)):
    if not current_user.department:
        raise HTTPException(status_code=400, detail="Head must be assigned to a department")
    
    # Count users in the department
    department_users_count = db.query(crud.models.User).filter(
        crud.models.User.department == current_user.department
    ).count()
    
    # Count events in the department
    department_events_count = db.query(crud.models.Event).filter(
        crud.models.Event.department == current_user.department
    ).count()
    
    # Count opportunities in the department
    department_opportunities_count = db.query(crud.models.Opportunity).filter(
        crud.models.Opportunity.department == current_user.department
    ).count()
    
    # Count confirmations for events in the department
    department_event_ids = db.query(crud.models.Event.id).filter(
        crud.models.Event.department == current_user.department
    ).all()
    department_event_ids = [event_id for (event_id,) in department_event_ids]
    
    department_confirmations_count = db.query(crud.models.EventConfirmation).filter(
        crud.models.EventConfirmation.event_id.in_(department_event_ids)
    ).count() if department_event_ids else 0
    
    # Get 5 most recent events in the department
    recent_events = db.query(crud.models.Event).filter(
        crud.models.Event.department == current_user.department
    ).order_by(crud.models.Event.created_at.desc()).limit(5).all()
    
    # Count upcoming events in the department
    now = datetime.utcnow()
    upcoming_events_count = db.query(crud.models.Event).filter(
        crud.models.Event.department == current_user.department,
        crud.models.Event.start_time > now
    ).count()
    
    return HeadDashboardData(
        department=current_user.department,
        department_users=department_users_count,
        department_events=department_events_count,
        department_opportunities=department_opportunities_count,
        department_confirmations=department_confirmations_count,
        recent_events=recent_events,
        upcoming_events=upcoming_events_count
    )

# Legacy dashboard endpoints (kept for backward compatibility)
@router.get("/dashboard/department_users/", response_model=List[UserRead])
def get_department_users(db: Session = Depends(get_db), current_user: UserRead = Depends(get_current_head_user)):
    users = db.query(crud.models.User).filter(crud.models.User.department == current_user.department).all()
    return users

@router.get("/dashboard/department_events/", response_model=List[EventRead])
def get_department_events(db: Session = Depends(get_db), current_user: UserRead = Depends(get_current_head_user)):
    events = db.query(crud.models.Event).filter(crud.models.Event.department == current_user.department).all()
    return events

# Event Management
@router.post("/events/", response_model=EventRead)
def create_event_head(event: EventCreate, db: Session = Depends(get_db), current_user: UserRead = Depends(get_current_head_user)):
    if event.department and event.department != current_user.department:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Heads can only create events for their own department.")
    
    return crud.create_event(db=db, event=event, creator_id=current_user.id, creator_role=current_user.role)

@router.get("/events/", response_model=List[EventRead])
def read_events_head(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: UserRead = Depends(get_current_head_user)):
    events = db.query(crud.models.Event).filter(crud.models.Event.department == current_user.department).offset(skip).limit(limit).all()
    return events

@router.get("/events/{event_id}", response_model=EventRead)
def read_event_head(event_id: UUID, db: Session = Depends(get_db), current_user: UserRead = Depends(get_current_head_user)):
    event = crud.get_event(db, event_id=event_id)
    if event is None:
        raise HTTPException(status_code=404, detail="Event not found")
    if event.department and event.department != current_user.department:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view events outside your department.")
    return event

@router.put("/events/{event_id}", response_model=EventRead)
def update_event_head(event_id: UUID, event_update: EventCreate, db: Session = Depends(get_db), current_user: UserRead = Depends(get_current_head_user)):
    db_event = crud.get_event(db, event_id=event_id)
    if db_event is None:
        raise HTTPException(status_code=404, detail="Event not found")
    
    if db_event.department and db_event.department != current_user.department:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Heads can only update events in their department.")
    if db_event.creator_id != current_user.id and db_event.creator_role not in [RoleEnum.EMPLOYEE, RoleEnum.STUDENT]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Heads can only update events created by themselves or lower roles.")

    return crud.update_event(db=db, db_event=db_event, event_update=event_update)

@router.delete("/events/{event_id}")
def delete_event_head(event_id: UUID, db: Session = Depends(get_db), current_user: UserRead = Depends(get_current_head_user)):
    db_event = crud.get_event(db, event_id=event_id)
    if db_event is None:
        raise HTTPException(status_code=404, detail="Event not found")
    
    if db_event.creator_role == RoleEnum.ADMIN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Events created by Admin cannot be deleted.")
    if db_event.creator_role not in [RoleEnum.HEAD, RoleEnum.EMPLOYEE, RoleEnum.STUDENT]:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Heads can only delete events created by themselves or lower roles.")
    if db_event.department and db_event.department != current_user.department:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Heads can only delete events in their department.")

    crud.delete_event(db, event_id=event_id)
    return {"message": "Event deleted successfully"}

@router.get("/events/calendar_view/", response_model=List[EventRead])
def get_events_for_calendar_head(
    start_time: datetime,
    end_time: datetime,
    db: Session = Depends(get_db),
    current_user: UserRead = Depends(get_current_head_user)
):
    query = db.query(crud.models.Event).filter(
        crud.models.Event.start_time >= start_time,
        crud.models.Event.start_time <= end_time,
        crud.models.Event.department == current_user.department
    )
    events = query.all()
    return events

# Opportunity Management
@router.post("/opportunities/", response_model=OpportunityRead)
def create_opportunity_head(opportunity: OpportunityCreate, db: Session = Depends(get_db), current_user: UserRead = Depends(get_current_head_user)):
    if opportunity.department and opportunity.department != current_user.department:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Heads can only create opportunities for their own department.")
    
    return crud.create_opportunity(db=db, opportunity=opportunity, posted_by_id=current_user.id, posted_by_role=current_user.role)

@router.get("/opportunities/", response_model=List[OpportunityRead])
def read_opportunities_head(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: UserRead = Depends(get_current_head_user)):
    opportunities = db.query(crud.models.Opportunity).filter(crud.models.Opportunity.department == current_user.department).offset(skip).limit(limit).all()
    return opportunities

@router.get("/opportunities/{opportunity_id}", response_model=OpportunityRead)
def read_opportunity_head(opportunity_id: UUID, db: Session = Depends(get_db), current_user: UserRead = Depends(get_current_head_user)):
    opportunity = crud.get_opportunity(db, opportunity_id=opportunity_id)
    if opportunity is None:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    if opportunity.department and opportunity.department != current_user.department:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Heads can only view opportunities in their department.")
    return opportunity

@router.put("/opportunities/{opportunity_id}", response_model=OpportunityRead)
def update_opportunity_head(opportunity_id: UUID, opportunity_update: OpportunityCreate, db: Session = Depends(get_db), current_user: UserRead = Depends(get_current_head_user)):
    db_opportunity = crud.get_opportunity(db, opportunity_id=opportunity_id)
    if db_opportunity is None:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    
    if db_opportunity.posted_by_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this opportunity")

    return crud.update_opportunity(db=db, db_opportunity=db_opportunity, opportunity_update=opportunity_update)

@router.delete("/opportunities/{opportunity_id}")
def delete_opportunity_head(opportunity_id: UUID, db: Session = Depends(get_db), current_user: UserRead = Depends(get_current_head_user)):
    db_opportunity = crud.get_opportunity(db, opportunity_id=opportunity_id)
    if db_opportunity is None:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    
    if db_opportunity.posted_by_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this opportunity")

    crud.delete_opportunity(db, opportunity_id=opportunity_id)
    return {"message": "Opportunity deleted successfully"}

# Event Confirmation
@router.get("/events/{event_id}/confirmations", response_model=List[EventConfirmationRead])
def get_event_confirmations_head(event_id: UUID, db: Session = Depends(get_db), current_user: UserRead = Depends(get_current_head_user)):
    event = crud.get_event(db, event_id=event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    if event.department and event.department != current_user.department:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Heads can only view confirmations for events in their department.")

    confirmations = crud.get_event_confirmations_for_event(db, event_id=event_id)
    return confirmations
