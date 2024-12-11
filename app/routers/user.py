from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from typing import Annotated
from sqlalchemy import select, insert, update, delete
from slugify import slugify


from app.backend.db_depends import get_db
from app.models import User
from app.schemas import CreateUser, UpdateUser

router = APIRouter(
    prefix="/user",
    tags=["user"]
)


DBSession = Annotated[Session, Depends(get_db)]

@router.get("/", status_code=status.HTTP_200_OK)
def all_users(db: DBSession):
    """Возвращает список всех пользователей."""
    query = select(User)
    users = db.scalars(query).all()
    return users

@router.get("/{user_id}", status_code=status.HTTP_200_OK)
def user_by_id(user_id: int, db: DBSession):
    """Возвращает пользователя по его ID."""
    query = select(User).where(User.id == user_id)
    user = db.scalar(query)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User was not found")
    return user

@router.post("/create", status_code=status.HTTP_201_CREATED)
def create_user(user: CreateUser, db: DBSession):
    """Создает нового пользователя."""

    slug = slugify(user.username)


    existing_user = db.scalar(select(User).where(User.username == user.username))
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User with this username already exists")


    new_user = User(
        username=user.username,
        firstname=user.firstname,
        lastname=user.lastname,
        age=user.age,
        slug=slug
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"status_code": status.HTTP_201_CREATED, "transaction": "Successful"}

@router.put("/update/{user_id}", status_code=status.HTTP_200_OK)
def update_user(user_id: int, user: UpdateUser, db: DBSession):
    """Обновляет данные пользователя."""
    query = select(User).where(User.id == user_id)
    existing_user = db.scalar(query)

    if existing_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User was not found")


    existing_user.firstname = user.firstname
    existing_user.lastname = user.lastname
    existing_user.age = user.age

    db.commit()

    return {"status_code": status.HTTP_200_OK, "transaction": "User update is successful!"}

@router.delete("/delete/{user_id}", status_code=status.HTTP_200_OK)
def delete_user(user_id: int, db: DBSession):
    """Удаляет пользователя по его ID."""
    query = select(User).where(User.id == user_id)
    existing_user = db.scalar(query)

    if existing_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User was not found")

    db.delete(existing_user)
    db.commit()

    return {"status_code": status.HTTP_200_OK, "transaction": "User deleted successfully"}