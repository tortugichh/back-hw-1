# ToDo FastAPI Project

This project is a ToDo application built with FastAPI, following a structured approach for better organization and maintainability.

## Project Structure

```
.
├── app/
│   ├── __init__.py
│   ├── main.py             # Main FastAPI application
│   ├── database.py         # Database connection and session management
│   ├── config.py           # Application configuration settings
│   ├── routers/
│   │   ├── __init__.py
│   │   └── tasks.py        # API endpoints for tasks
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── tasks.py        # Pydantic models for request/response validation
│   ├── models/
│   │   ├── __init__.py
│   │   └── tasks.py        # SQLAlchemy models for database tables
│   ├── crud/
│   │   ├── __init__.py
│   │   └── tasks.py        # CRUD operations for tasks
│   └── utils/
│       ├── __init__.py
│       └── auth.py         # Utility functions (e.g., authentication)
├── tests/
│   ├── __init__.py
│   └── test_tasks.py       # Unit and integration tests for tasks
├── requirements.txt      # Python dependencies
└── .gitignore            # Git ignore file
```

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
