"""FastAPI application entrypoint for MirrorAI's local vision backend."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from python.routers.experience import router as experience_router
from python.routers.face import router as face_router
from python.routers.salon import router as salon_router


app = FastAPI(
    title="MirrorAI Local Vision Backend",
    description="Self-hosted FastAPI backend scaffold for future virtual salon AI modules.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(experience_router)
app.include_router(face_router)
app.include_router(salon_router)
