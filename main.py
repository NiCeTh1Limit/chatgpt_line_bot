from fastapi import FastAPI
from routers import line
app = FastAPI()
app.include_router(line.router)