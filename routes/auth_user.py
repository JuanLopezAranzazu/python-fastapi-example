from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError
from passlib.context import CryptContext
from datetime import datetime, timedelta

from db.database import SessionLocal
from sqlalchemy.orm import Session
from db.models import models

# http://127.0.0.1:8000/auth_users

ALGORITHM = "HS256"
ACCESS_TOKEN_DURATION = 1
SECRET = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"

router = APIRouter(prefix="/auth_users", tags=["auth_users"])

oauth2 = OAuth2PasswordBearer(tokenUrl="login")

crypt = CryptContext(schemes=["bcrypt"])

def get_db():
  try:
    db = SessionLocal()
    yield db
  finally:
    db.close()

# api autenticacion de usuarios

def search_user(email: str, db: Session = Depends(get_db)):
  return db.query(models.User).filter(models.User.email == email).first()


async def auth_user(token: str = Depends(oauth2), db: Session = Depends(get_db)):
  
  exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, 
                        detail="El usuario no esta autenticado",
                        headers={"WWW-Authenticate":"Bearer"})
  
  try:
    email = jwt.decode(token, SECRET, algorithms=ALGORITHM).get("sub")
    if (email is None):
      raise exception
    
  except JWTError:
    raise exception
  
  return search_user(email, db)

async def current_user(user: models.User = Depends(auth_user)):
  if (not user.is_active):
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                        detail="El usuario esta inactivo")
  
  return user


# login de usuarios

@router.post("/login")
async def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
  user_found = search_user(form.username, db)
  if (not user_found):
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                        detail="El correo no es correcto")
  
  if (not crypt.verify(form.password, user_found.password)):
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                        detail="La contraseña es incorrecta")
  
  expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_DURATION)
  access_token = {"sub":user_found.email,"exp":expire}
  
  return { 
    "access_token": jwt.encode(access_token, SECRET, algorithm=ALGORITHM),
    "token_type": "bearer" 
  }

# obtener el usuario autenticado

@router.get("/authenticate")
async def authenticate(user: models.User = Depends(current_user)):
  return user


