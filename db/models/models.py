from sqlalchemy import Column, Integer, String, Boolean
from db.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255))
    password = Column(String(255))
    is_active = Column(Boolean, default=True)
  
