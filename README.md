# 📚 Bookly – FastAPI Beyond CRUD

Bookly is a **production-ready backend API** built with **FastAPI**, going far beyond basic CRUD operations.  
It demonstrates **clean architecture**, **async SQLModel**, **JWT authentication**, **email workflows**, **Role-based access control**, **custom logging**, and **robust error handling**.

> 🚀 Built as a learning + real-world backend project.

---

## ✨ Features

### 🔐 Authentication & Security

- User registration & login
- JWT access & refresh tokens
- Email verification flow
- Password reset (token-based)
- Role-Based Access Control (RBAC)
- Custom authentication middleware

### 👤 User Management

- User account creation
- Email verification
- Password reset & change
- User-level logging

### 📖 Books & Reviews

- Books CRUD
- Reviews system
- User ↔ Book relationships
- Async DB operations

### 📬 Email Support

- Account verification email
- Password reset email
- Password reset success email
- HTML templates using **Jinja2**
- Background email sending

### 🧠 Architecture

- Modular project structure
- REST-based API end points
- Service layer abstraction
- Repository-style DB access
- Centralized exception handling
- Middleware-driven auth & logging

### 📊 Logging

- App-level logs (`app.log`)
- User-specific logs (`<username>.log`)
- Request lifecycle logging
- Error & performance logging

### 🧪 Testing

- Pytest setup
- Fixtures via `conftest.py`
- Dependency overrides
- Service mocking

---

## 🗂️ Project Structure

```text
bookly/
|
├── database/                     # Database engine, sessions, and persistence layer
│   ├── auth/                     # User authentication & authorization database logic
│   │   ├── models.py             # User-related database models
│   │   └── schemas.py            # User-related request/response schemas
│   ├── books/                    # Books domain database logic
│   │   ├── models.py             # Book-related database models
│   │   └── schemas.py            # Book-related request/response schemas
│   ├── reviews/                  # Reviews domain database logic
│   │   ├── models.py             # Review-related database models
│   │   └── schemas.py            # Review-related request/response schemas
│   ├── main.py                   # Database engine and session management
│   ├── models.py                 # Shared / base database models
│   └── redis.py                  # Redis connection and cache utilities
│── logger/                       # App & user loggers
|── logs/                         # App and User Logs
|   └── user_logs/
|       ├── <<user_1>>.log        # User specific logs
|       ├── <<user_2>>.log        # User specific logs
|   └── app.log                   # Centralized application log
├── migration/                    # Alembic database migration files
│   ├── versions/                 # Auto-generated migration versions
│   ├── env.py                    # Alembic environment and migration configuration
│   ├── README.md                 # Alembic usage and migration instructions
│   └── script.py.mako            # Alembic migration script template
├── src/
│   ├── auth/                     # Authentication & JWT logic
│   ├── users/                    # User models, services, routes
│   ├── books/                    # Book models, services, routes
│   ├── reviews/                  # Reviews models, services, routes
│   ├── email/                    # Email service & templates
│   │   └── templates/
│   │       ├── verify_account.html
│   │       ├── password_reset.html
│   │       └── password_reset_success.html
│   │   └── mail.py               #Email service
│   ├
│   ├── middleware.py             # Auth & logging middleware
│   ├── error.py                  # Custom exceptions, errors & handlers
│   ├── tests/                    # Pytest tests
│   │   └── conftest.py           # Pytests configtest.py file
│   │   └── other_tests.py
│
├── .env                          # Environment variables
├── .gitignore                    # Git ignore rules
├── alembic.ini                   # Alembic configuration file
├── config.py                     # Application environment configuration
|── main.py                       # FastAPI app entry point
├── requirements.txt
├── README.md                     # The file you are currently reading 😉
├── run_app.sh                    # bash file to run the application
```

## App running in dev mode

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
fastapi dev main.py
```
