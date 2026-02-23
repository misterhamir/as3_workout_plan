from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from app.modules.workoutAdvisor.router import workout_router

app = FastAPI()

app.include_router(workout_router)


@app.get("/")
def root():
    return RedirectResponse(url="/workout-advisor")
