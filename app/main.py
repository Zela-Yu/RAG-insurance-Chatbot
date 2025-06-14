import os
from dotenv import load_dotenv
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "../.env"))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.router import router
from app.retriever import initialize_index

from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize_index()
    yield

app = FastAPI(lifespan=lifespan)
app.include_router(router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files
frontend_path = os.path.join(os.path.dirname(__file__), "../static")
app.mount("/static", StaticFiles(directory=frontend_path), name="static")

# Serve index.html at root
@app.get("/")
def read_index():
    return FileResponse(os.path.join(frontend_path, "index.html"))

