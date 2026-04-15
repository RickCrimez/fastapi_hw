from fastapi import FastAPI
from app.database import engine, Base
from app.routers import advertisements

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Advertisement Service", version="1.0.0")

app.include_router(advertisements.router)

@app.get("/")
def root():
    return {"message": "Advertisement Service is running"}