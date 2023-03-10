from fastapi import FastAPI
from routes import user, auth_user

app = FastAPI()

# uvicorn main:app --reload
# http://127.0.0.1:8000

@app.get("/")
async def root():
  return { "message": "API USERS MYSQL" }
   
   
# routes
app.include_router(user.router)
app.include_router(auth_user.router)

