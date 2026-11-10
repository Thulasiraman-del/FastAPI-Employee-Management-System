# Employee Management System

A role-based Employee Management System built with Python, Django, Django REST Framework, and SQLite, with optional PostgreSQL configuration.

The project provides REST APIs for managing employees, departments, attendance, leave requests, and administrative reports.

## Features

### Authentication and Authorization
- JWT authentication using Simple JWT.
- Role-based access control.
- Custom user model.
- Admin, HR, Manager, and Employee roles.
- Protected administrative endpoints.

### Employee Management
- Create, retrieve, update, and deactivate employees.
- Department association.
- Employee search, filtering, and ordering.
- Email normalization and duplicate validation.
- Soft deletion to preserve employee history.

### Department Management
- Department CRUD operations.
- Unique department names and codes.
- Active/inactive department status.
- Search and filtering.

### Attendance Management
- Daily employee attendance records.
- Present, Late, Half Day, and Absent statuses.
- Check-in and check-out validation.
- Duplicate attendance prevention.
- Attendance filtering and reporting.

### Leave Management
- Employee leave applications.
- Automatic employee profile association.
- Pending, Approved, and Rejected statuses.
- HR/Admin approval and rejection.
- Review comments and timestamps.
- Employees can access their own leave requests.

### Reports
- Administrative dashboard statistics.
- Employee CSV export.
- Attendance CSV export.
- CSV formula-injection protection.

## Technology Stack

| Category | Technology |
|---|---|
| Language | Python |
| Backend | Django |
| API | Django REST Framework |
| Authentication | Simple JWT |
| Database | SQLite |
| Optional database | PostgreSQL |
| Filtering | django-filter |
| API documentation | drf-spectacular |
| Testing | Django Test Framework / pytest-django |

## Project Structure

```text
FastAPI-Employee-Management-System/
|
|-- accounts/
|-- attendance/
|-- config/
|-- departments/
|-- employees/
|-- leave_management/
|-- reports/
|
|-- manage.py
|-- requirements.txt
|-- requirements-django.txt
|-- .env.example
|-- openapi-schema.yml
|
|-- main.py
|-- auth.py
|-- auth_schemas.py
|-- crud.py
|-- database.py
|-- models.py
|-- schemas.py
```

The original FastAPI implementation is preserved in the root-level Python files. The Django implementation is organized into separate applications.

## Installation and Setup

### 1. Clone the repository

```bash
git clone --branch feature/django-migration https://github.com/Thulasiraman-del/FastAPI-Employee-Management-System.git
cd FastAPI-Employee-Management-System
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. Install Django dependencies

```bash
python -m pip install -r requirements-django.txt
```

### 4. Configure environment variables

```powershell
Copy-Item .env.example .env
```

Update `.env` with a strong, randomly generated Django secret key.

The default database configuration uses SQLite.

PostgreSQL can be configured using the database environment variables documented in `.env.example`.

### 5. Apply migrations

```bash
python manage.py migrate
```

### 6. Create an administrator

```bash
python manage.py createsuperuser
```

### 7. Start the development server

```bash
python manage.py runserver
```

The application will be available at:

```text
http://127.0.0.1:8000/
```

## Authentication

JWT authentication endpoints:

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/api/auth/token/` | Obtain access and refresh tokens |
| POST | `/api/auth/token/refresh/` | Refresh access token |

For protected API requests, include:

```http
Authorization: Bearer <access_token>
```

## API Documentation

After starting the development server:

- Swagger UI: `/api/docs/`
- ReDoc: `/api/redoc/`
- OpenAPI schema: `/api/schema/`

The generated schema is also maintained in `openapi-schema.yml`.

## Testing

Run the complete Django test suite:

```bash
python manage.py test
```

Check Django configuration:

```bash
python manage.py check
```

Check migration consistency:

```bash
python manage.py makemigrations --check --dry-run
```

Validate the OpenAPI schema:

```bash
python manage.py spectacular --validate --file openapi-schema.yml
```

## Security Practices

- JWT-based authentication.
- Role-based API permissions.
- Environment-based secret configuration.
- Protected administrative endpoints.
- Input validation through serializers.
- CSV formula-injection mitigation.
- Soft deletion of employee records.
- Database transaction handling for leave reviews.

For production deployment, configure HTTPS, secure cookies, a production-grade secret key, appropriate allowed hosts, and PostgreSQL settings.

## Current Development Status

- Django REST API implementation completed.
- Authentication and role-based permissions implemented.
- Employee, department, attendance, and leave modules implemented.
- Dashboard and CSV reports implemented.
- Automated test suite and OpenAPI validation available.

## License

No license has been specified yet.
