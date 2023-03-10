from pydantic import BaseModel
from typing import Optional

# entidades

class UserCreate(BaseModel):
  email: str
  password: str

class User(UserCreate):
  id: Optional[int]
  is_active: Optional[bool] 
  
  class Config:
    orm_mode = True

