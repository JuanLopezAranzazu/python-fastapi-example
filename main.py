from fastapi import FastAPI
from routes import user

app = FastAPI()

# uvicorn main:app --reload
# http://127.0.0.1:8000

@app.get("/")
async def root():
  return { "message": "API USERS MYSQL" }
   
   
# routes
app.include_router(user.router)

