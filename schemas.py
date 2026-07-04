from pydantic import BaseModel, Field, EmailStr


class Employee_Create(BaseModel):
    id: int = Field(gt=0)
    name: str = Field(min_length=1, max_length=50)
    position: str = Field(min_length=2, max_length=50)
    salary: int = Field(gt=1000)
    department: str = Field(min_length=2, max_length=50)
    email: EmailStr
    phone: str = Field(min_length=10, max_length=10)


class Employee_response(BaseModel):
    id: int
    name: str
    position: str
    salary: int
    department: str
    email: EmailStr
    phone: str

    class Config:
        from_attributes = True