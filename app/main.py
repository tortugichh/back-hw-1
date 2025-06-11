from fastapi import FastAPI

from app.routers import tasks, auth
# from app.database import get_db
# from app.auth import verify_token
# from app.crud import users as crud_users
# from app.models.users import User

# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/token")

app = FastAPI(
    title="ToDo API",
    description="A simple ToDo application with FastAPI",
    version="1.0.0",
)


# async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
#     credentials_exception = HTTPException(
#         status_code=status.HTTP_401_UNAUTHORIZED,
#         detail="Could not validate credentials",
#         headers={"WWW-Authenticate": "Bearer"},
#     )
#     username = verify_token(token, credentials_exception)
#     user = crud_users.get_user_by_username(db, username=username)
#     if user is None:
#         raise credentials_exception
#     return user


app.include_router(tasks.router, prefix="/api/v1", tags=["tasks"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
