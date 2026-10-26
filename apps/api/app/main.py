from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.adjust import router as adjust_router
from app.admin import router as admin_router
from app.catalog import router as catalog_router
from app.coach import router as coach_router
from app.config import settings
from app.cycle import router as cycle_router
from app.metrics import router as metrics_router
from app.nutrition import router as nutrition_router
from app.planner import router as planner_router
from app.progress import router as progress_router
from app.reminders import router as reminders_router
from app.routers import router
from app.tasks_routes import router as tasks_router
from app.workouts import router as workouts_router

app = FastAPI(title="Levefit API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.cors_origins.split(",") if o.strip()],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router)
app.include_router(tasks_router)
app.include_router(workouts_router)
app.include_router(metrics_router)
app.include_router(adjust_router)
app.include_router(coach_router)
app.include_router(catalog_router)
app.include_router(cycle_router)
app.include_router(planner_router)
app.include_router(nutrition_router)
app.include_router(admin_router)
app.include_router(progress_router)
app.include_router(reminders_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
