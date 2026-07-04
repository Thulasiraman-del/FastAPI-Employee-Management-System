from sqlalchemy.orm import Session
import models
import schemas


def createemployee(db: Session, employee: schemas.Employee_Create):
    db_employee = models.Employee(**employee.model_dump())
    db.add(db_employee)
    db.commit()
    db.refresh(db_employee)
    return db_employee


def get_employee(db: Session, employee_id: int):
    return db.query(models.Employee).filter(models.Employee.id == employee_id).first()


def get_all_employees(db: Session):
    return db.query(models.Employee).all()


def update_employee(db: Session, employee_id: int, employee: schemas.Employee_Create):
    db_employee = db.query(models.Employee).filter(models.Employee.id == employee_id).first()

    if not db_employee:
        return None

    db_employee.name = employee.name
    db_employee.position = employee.position
    db_employee.department = employee.department
    db_employee.salary = employee.salary
    db_employee.email = employee.email
    db_employee.phone = employee.phone

    db.commit()
    db.refresh(db_employee)

    return db_employee


def delete_employee(db: Session, employee_id: int):
    db_employee = db.query(models.Employee).filter(models.Employee.id == employee_id).first()

    if not db_employee:
        return None

    db.delete(db_employee)
    db.commit()

    return db_employee