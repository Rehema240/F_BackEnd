from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from event_api.models import Base, User
from event_api.dependencies import get_db, engine
from event_api.auth import verify_password, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from typing import List
from fastapi.middleware.cors import CORSMiddleware

from event_api.routers import admin, head, employee, student, auth

app = FastAPI(
    title="Event Management API",
    description="API for managing events, opportunities, users, and notifications with role-based access control.",
    version="1.0.0",
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Create database tables
Base.metadata.create_all(bind=engine)

# Include routers
app.include_router(admin.router)
app.include_router(head.router)
app.include_router(employee.router)
app.include_router(student.router)

@app.get("/")
async def read_root():
    return {"message": "Welcome to the Event API!"}

app.include_router(auth.router)
