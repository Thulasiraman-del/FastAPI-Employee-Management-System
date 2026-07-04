from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm

import schemas
import models
import crud
import auth

from auth import get_current_user
from auth_schemas import CreateUser, UserLogin, Token
from database import SessionLocal, engine

app = FastAPI()

models.Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def read_root():
    return {"message": "Welcome to EMS"}


@app.post("/register")
def register_user(user: CreateUser, db: Session = Depends(get_db)):
    existing_user = db.query(models.User).filter(
        models.User.username == user.username
    ).first()

    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")

    hashed_password = auth.hash_password(user.password)

    new_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "User registered successfully"}


@app.post("/login", response_model=Token)
def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    db_user = db.query(models.User).filter(
        models.User.username == form_data.username
    ).first()

    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    if not auth.verify_password(form_data.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    access_token = auth.create_access_token(data={"sub": db_user.username})

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@app.get("/employees", response_model=list[schemas.Employee_response])
def get_all_employees(
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    return crud.get_all_employees(db)


@app.get("/employees/{id}", response_model=schemas.Employee_response)
def get_employees_by_id(
    id: int,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    employee = crud.get_employee(db, id)

    if employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")

    return employee


@app.post("/employees", response_model=schemas.Employee_response)
def create_employee(
    employee: schemas.Employee_Create,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    return crud.createemployee(db, employee)


@app.put("/employees/{id}", response_model=schemas.Employee_response)
def update_employee(
    id: int,
    employee: schemas.Employee_Create,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    updated_employee = crud.update_employee(db, id, employee)

    if updated_employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")

    return updated_employee


@app.delete("/employees/{id}")
def delete_employee(
    id: int,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    employee = crud.delete_employee(db, id)

    if employee is None:
        raise HTTPException(status_code=404, detail="Employee not found")

    return {"message": "Employee deleted successfully"}