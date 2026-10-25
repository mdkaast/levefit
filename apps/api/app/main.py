from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.metrics import router as metrics_router
from app.routers import router
from app.workouts import router as workouts_router

app = FastAPI(title="PFO API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.cors_origins.split(",") if o.strip()],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router)
app.include_router(workouts_router)
app.include_router(metrics_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
