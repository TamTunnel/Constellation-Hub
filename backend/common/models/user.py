"""
User model for authentication.
"""
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base

# Create a local Base for auth models
# In production, this should be imported from the service's db module
Base = declarative_base()


class UserORM(Base):
    """SQLAlchemy ORM model for users."""
    
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False, default="viewer")  # viewer, operator, admin
    is_active = Column(Boolean, default=True)
    api_key = Column(String(255), unique=True, nullable=True)  # Optional API key
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', role='{self.role}')>"
