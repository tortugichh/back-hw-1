# ToDo FastAPI Project, Without deploy(жду аппрува гитхаб едукейшн для digital ocean)



This project is a ToDo application built with FastAPI, following a structured approach for better organization and maintainability.

## Setup Instructions

1.  **Create a virtual environment** (recommended):
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

2.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the application**:
    ```bash
    uvicorn app.main:app --reload
    ```

## API Documentation

The API documentation will be available at `/docs` (Swagger UI) and `/redoc` (ReDoc) after running the application.

## Project Structure

```
.
├── app/
│   ├── __init__.py
│   ├── main.py             # Main FastAPI application
│   ├── auth.py             # JWT authentication logic (hashing, token creation/verification)
│   ├── cache.py            # Redis client setup and caching utilities
│   ├── celery_app.py       # Celery application configuration
│   ├── config.py           # Application settings and environment variable loading
│   ├── database.py         # SQLAlchemy engine, session, and database dependency
│   ├── dependencies.py     # Common FastAPI dependencies (e.g., get_current_user)
│   ├── crud/               # Database Create, Read, Update, Delete operations
│   │   ├── __init__.py
│   │   ├── tasks.py        # CRUD for tasks
│   │   └── users.py        # CRUD for users
│   ├── models/             # SQLAlchemy and Pydantic models
│   │   ├── __init__.py
│   │   ├── tasks.py        # SQLAlchemy model for tasks
│   │   └── users.py        # SQLAlchemy and Pydantic models for users
│   ├── routers/            # FastAPI routers for API endpoints
│   │   ├── __init__.py
│   │   ├── auth.py         # Authentication endpoints (register, login)
│   │   └── tasks.py        # Task-related endpoints (create, read, update, delete)
│   ├── schemas/            # Pydantic schemas for request/response validation
│   │   ├── __init__.py
│   │   └── tasks.py        # Schemas for tasks
│   └── tasks.py            # Celery background tasks
├── .env                    # Environment variables (e.g., DATABASE_URL, REDIS_URL, SECRET_KEY)
├── Dockerfile              # Dockerfile for building the FastAPI application image
├── docker-compose.yml      # Docker Compose configuration for multi-service setup (FastAPI, PostgreSQL, Redis, Celery)
├── requirements.txt        # Python dependencies
├── alembic.ini             # Alembic configuration for database migrations
├── alembic/                # Alembic migration scripts
├── .gitignore              # Git ignore file
└── README.md               # Project README and documentation
```
