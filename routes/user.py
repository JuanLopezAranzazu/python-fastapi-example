from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from db.models import models
from db.schemas import schemas
from db.database import SessionLocal, engine

router = APIRouter(prefix="/users", tags=["users"])

models.Base.metadata.create_all(bind=engine)

crypt = CryptContext(schemes=["bcrypt"])


def get_db():
  try:
    db = SessionLocal()
    yield db
  finally:
    db.close()
    
# http://127.0.0.1:8000/users

# api usuarios

@router.get("/", response_model=List[schemas.User])
async def get_users(db: Session = Depends(get_db)):
  return db.query(models.User).all()


@router.get("/query/", response_model=List[schemas.User])
async def get_users_filter(is_active: bool, db: Session = Depends(get_db)):
  return db.query(models.User).filter(models.User.is_active == is_active).all()


@router.get("/{id}", response_model=schemas.User)
async def get_user(id: int, db: Session = Depends(get_db)):
  user_model = db.query(models.User).filter(models.User.id == id).first()

  if user_model is None:
      raise HTTPException(
          status_code=status.HTTP_404_NOT_FOUND,
          detail=f"El usuario con el id {id} no existe"
      )
  
  return user_model


@router.post("/", response_model=schemas.User, status_code=status.HTTP_201_CREATED)
async def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):

    user_found = db.query(models.User).filter(models.User.email == user.email).first()
    
    if user_found:
      raise HTTPException(
          status_code=status.HTTP_400_BAD_REQUEST,
          detail=f"El usuario con el email {user.email} ya existe"
      )
    
    user_model = models.User()
    user_model.email = user.email
    user_model.password = crypt.hash(user.password)

    db.add(user_model)
    db.commit()

    return user_model

@router.put("/{id}", response_model=schemas.User)
async def update_user(id: int, user: schemas.User, db: Session = Depends(get_db)):

    user_model = db.query(models.User).filter(models.User.id == id).first()

    if user_model is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"El usuario con el id {id} no existe"
        )

    user_model.email = user.email
    user_model.password = crypt.hash(user.password)

    if ("is_active" in dict(user)):
      user_model.is_active = user.is_active


    db.add(user_model)
    db.commit()

    return user_model


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(id: int, db: Session = Depends(get_db)):

    user_model = db.query(models.User).filter(models.User.id == id).first()

    if user_model is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"El usuario con el id {id} no existe"
        )

    db.query(models.User).filter(models.User.id == id).delete()

    db.commit()

