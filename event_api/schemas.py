from datetime import datetime
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, EmailStr

from event_api.models import RoleEnum, ConfirmationStatusEnum, NotificationTypeEnum

# ---------- User ----------
class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: Optional[str]
    department: Optional[str]

class UserCreate(UserBase):
    password: str
    role: RoleEnum = RoleEnum.STUDENT

class UserRead(UserBase):
    id: UUID
    role: RoleEnum
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

# ---------- Event ----------
class EventBase(BaseModel):
    title: str
    description: Optional[str]
    location: Optional[str]
    department: Optional[str]
    start_time: datetime
    end_time: Optional[datetime]
    capacity: Optional[int]
    is_public: Optional[bool] = True

class EventCreate(EventBase):
    # creator info is set by server from token
    pass

class EventRead(EventBase):
    id: UUID
    creator_id: Optional[UUID]
    creator_role: RoleEnum
    confirmation_count: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

# ---------- Opportunity ----------
class OpportunityBase(BaseModel):
    title: str
    description: Optional[str]
    link: Optional[str]
    department: Optional[str]

class OpportunityCreate(OpportunityBase):
    pass

class OpportunityRead(OpportunityBase):
    id: UUID
    posted_by_id: Optional[UUID]
    posted_by_role: RoleEnum
    created_at: datetime

    class Config:
        from_attributes = True

# ---------- EventConfirmation ----------
class EventConfirmationBase(BaseModel):
    note: Optional[str]

class EventConfirmationCreate(EventConfirmationBase):
    event_id: UUID
    status: Optional[ConfirmationStatusEnum] = ConfirmationStatusEnum.CONFIRMED

class EventConfirmationRead(EventConfirmationBase):
    id: UUID
    event_id: UUID
    student_id: UUID
    status: ConfirmationStatusEnum
    confirmed_at: datetime

    class Config:
        from_attributes = True

# ---------- Notification ----------
class NotificationBase(BaseModel):
    title: str
    body: Optional[str]
    type: NotificationTypeEnum

class NotificationCreate(NotificationBase):
    recipient_id: UUID
    related_event_id: Optional[UUID]
    related_opportunity_id: Optional[UUID]

class NotificationRead(NotificationBase):
    id: UUID
    recipient_id: UUID
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True

# ---------- Authentication ----------
class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str
