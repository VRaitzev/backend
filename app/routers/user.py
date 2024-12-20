from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select
from app.core.database import get_db
from app.models.user import User
from app.models.physical_plan import PhysicalPlan
from app.models.workout import Workout, WorkoutExercise, Exercise
from app.models.mental_plan import MentalPlan, MentalPlanResource, Resource
from app.models.outher_task import OuterTask
from app.auth.hash_password import HashPassword
from app.auth.jwt_handler import create_access_token
from pydantic import BaseModel

from app.auth.authenticate import authenticate

hash_password = HashPassword()


router = APIRouter()

# Схема для валидации входящих данных
class UserCreate(BaseModel):
    login: str
    password: str

class UserSignIn(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user_id: int


@router.post("/users/", response_model=dict)
async def create_user(user_data: UserCreate, db: AsyncSession = Depends(get_db)):
    new_user = User(
        login=user_data.login,
        password=hash_password.create_hash(user_data.password)
    )
    try:
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        access_token = create_access_token(user_data.login)
        return {"access_token": access_token, "token_type": "Bearer", "user_id": new_user.id}
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=400, detail="User with this login already exists")
    
    



@router.post("/users/signIn", response_model=TokenResponse | dict)
async def sign_user_in(data: UserSignIn, session: AsyncSession = Depends(get_db)) -> dict:
    quare = select(User).where(User.login == data.username)
    result = await session.execute(quare)
    user = result.scalar()
    if not user:
        raise HTTPException(
        status_code=404, detail="User does not exist")
    if not hash_password.verify_hash(data.password, user.password):
        raise HTTPException(
        status_code=403, detail="Wrong credential passed")
    access_token = create_access_token(data.username)
    return {"access_token": access_token, "token_type": "Bearer", "user_id": user.id}




@router.get("/users/{user_id}/physical-plan")
async def get_physical_plan(user_id: int, user: str = Depends(authenticate), db: AsyncSession = Depends(get_db)):
    """
    Получить физический план по ID пользователя.
    """
    try:
        # Получаем физический план пользователя
        query = await db.execute(select(PhysicalPlan).where(PhysicalPlan.user_id == user_id))
        physical_plan = query.scalars().first()

        if not physical_plan:
            raise HTTPException(status_code=404, detail="Physical plan not found")

        # Получаем тренировки, связанные с этим планом
        query = await db.execute(select(Workout).where(Workout.physical_plan_id == physical_plan.id))
        workouts = query.scalars().all()

        # Формируем ответ
        physical_plan_res = {
            "data": physical_plan,
            "user_id": physical_plan.user_id,
            "days": []
        }

        for workout in workouts:
            # Получаем упражнения для конкретной тренировки
            query = await db.execute(select(WorkoutExercise).where(WorkoutExercise.workout_id == workout.id))
            workout_exercises = query.scalars().all()

            exercises = []
            for workout_exercise in workout_exercises:
                # Получаем детали упражнения
                query = await db.execute(select(Exercise).where(Exercise.id == workout_exercise.exercise_id))
                exercise = query.scalars().first()
                if exercise:
                    exercises.append(exercise)

            physical_plan_res["days"].append({
                "workout_id": workout.id,
                "day_of_week": workout.day_of_week,
                "exercises": exercises
            })

        return physical_plan_res

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
    

@router.get("/users/{user_id}/mental-plan")
async def get_mental_plan(user_id: int, user: str = Depends(authenticate), db: AsyncSession = Depends(get_db)):
    try:
        query = await db.execute(select(MentalPlan).where(MentalPlan.user_id == user_id))
        mental_plan = query.scalars().first()
        if not mental_plan:
            raise HTTPException(status_code=404, detail="Mental plan not found")
        print("SIGN")
        query = await db.execute(
            select(Resource, MentalPlanResource.progress)
            .join(MentalPlanResource, MentalPlanResource.resource_id == Resource.id)
            .where(MentalPlanResource.mental_plan_id == mental_plan.id)
            )

        results = query.all()
        mental_plan_res = {
            "data": mental_plan,
            "user_id": mental_plan.user_id,
            "resources": [{"resource": resource, "progress": progress} for resource, progress in results]
        }

        return mental_plan_res
    except HTTPException:
        raise 
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")
    
@router.get("/users/{user_id}/outer-tasks")
async def get_outher_tasks(user_id: int, user: str = Depends(authenticate), db: AsyncSession = Depends(get_db)):
    try:
        query = await db.execute(select(OuterTask).where(OuterTask.user_id == user_id))
        outer_tasks = query.scalars().all()
        if not outer_tasks:
            raise HTTPException(status_code=404, detail="Outher tasks not found")
        print("SIGN")
        return outer_tasks
    except HTTPException:
        raise 
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")
