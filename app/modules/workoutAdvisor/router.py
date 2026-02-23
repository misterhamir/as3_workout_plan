from typing import Literal, Optional

import markdown
from fastapi import APIRouter, Form, Request
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field

from app.utils.openai import client
from app.utils.tools import calculate_bmi

from .prompt import SYSTEM_PROMPT

template = Jinja2Templates(directory="templates")

MODEL = "minimax/minimax-m2.5"
workout_router = APIRouter(prefix="/workout-advisor", tags=["workout-advisor"])


class Workout(BaseModel):
    workout_name: str = Field(description="Name of the workout or exercise")
    muscle_group: str = Field(description="Primary muscle group targeted by the workout")
    equipment_needed: str = Field(description="Equipment required for the workout, if any")
    reps_or_duration: int = Field(description="Recommended number of repetitions or duration in seconds")
    sets: int = Field(description="Number of sets to perform")


class WorkoutPlan(BaseModel):
    goal_summary: str = Field(description="One sentence describing the fitness goal")
    weekly_schedule: str = Field(description="Structured breakdown of workouts by day")
    workouts: list[Workout] = Field(description="List of workout exercises")
    key_tips: str = Field(description="Important advice for the workout plan")


class Meal(BaseModel):
    meal_name: str = Field(description="Name of the meal or food item")
    calories: int = Field(description="Estimated calorie content of the meal")
    protein_g: int = Field(description="Amount of protein in grams")
    carbs_g: int = Field(description="Amount of carbohydrates in grams")
    fats_g: int = Field(description="Amount of fats in grams")


class NutritionPlan(BaseModel):
    calorie_target: int = Field(description="Estimated daily calorie target")
    macros_breakdown: str = Field(description="Protein/carbs/fats breakdown in grams")
    meals: list[Meal] = Field(description="Sample daily meal plan")
    foods_to_prioritize: str = Field(description="List of recommended foods")
    foods_to_avoid: str = Field(description="List of foods to limit or avoid")


class AdvisorResponse(BaseModel):
    intent: Literal["workout_plan", "nutrition_plan", "assessment", "general_knowledge", "out_of_scope"]
    workout_plan: Optional[WorkoutPlan] = None
    nutrition_plan: Optional[NutritionPlan] = None
    free_response: Optional[str] = None


@workout_router.get("/")
def get_workout_advisor(request: Request):
    return template.TemplateResponse("index.html", {"request": request, "model": MODEL})


@workout_router.post("/")
def post_workout_advisor(
    request: Request,
    weight: float = Form(...),
    height: float = Form(...),
    age: int = Form(...),
    user_input: str = Form(...),
):
    bmi_data = calculate_bmi(weight, height)
    user_message = (
        f"User profile: {weight}kg, {height}cm, {age} years old, "
        f"BMI: {bmi_data['bmi']} ({bmi_data['category']})\n\n"
        f"Goals/limitations: {user_input}"
    )

    completion = client.beta.chat.completions.parse(
        model=MODEL,
        messages=[{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": user_message}],
        response_format=AdvisorResponse,
    )

    result = completion.choices[0].message.parsed
    if result is None:
        raise ValueError("Failed to parse response")

    response_data = {
        "intent": result.intent,
        "workout_plan": result.workout_plan.model_dump() if result.workout_plan else None,
        "nutrition_plan": result.nutrition_plan.model_dump() if result.nutrition_plan else None,
        "free_response": markdown.markdown(result.free_response) if result.free_response else None,
    }

    return template.TemplateResponse(
        "index.html", {
            "request": request,
            "response": response_data,
            "user_input": user_input,
            "model": MODEL,
            "bmi": bmi_data,
            "weight": weight,
            "height": height,
            "age": age,
        }
    )
