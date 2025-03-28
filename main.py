import config
import uvicorn
from datetime import timedelta

from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from src.auth.auth import (
    create_access_token, authenticate_user, get_current_user
)
from src.db.db import get_db, UserDB, create_initial_users
from src.ml.ml import get_ml_service
from src.models.models import InputData, User

app = FastAPI()

SECRET_KEY = "123456"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@app.on_event("startup")
async def startup_event():
    db = next(get_db())
    create_initial_users(db)


@app.on_event("shutdown")
async def shutdown_event():
    pass


@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    db = next(get_db())
    user = await authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


def role_required(role: str):
    def decorator(func):
        async def wrapper(*args, **kwargs):
            user = await get_current_user()  # Получаем текущего пользователя
            if user.role != role:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Доступ запрещен"
                )
            return await func(*args, **kwargs)

        return wrapper

    return decorator


@app.post("/model_fit")
@role_required("admin")
async def model_fit(user: User = Depends(get_current_user)):
    try:
        model = get_ml_service(config.BASE_DIR)
        model.create_model()
        return {"message": "Model successfully trained and saved"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/predict")
async def predict(data: InputData, user: User = Depends(get_current_user)):
    model = get_ml_service(config.BASE_DIR)
    features = [[data.feature1, data.feature2, data.feature3, data.feature4]]
    prediction = model.predict(features)
    prediction = prediction.tolist()
    return {"prediction": prediction}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
