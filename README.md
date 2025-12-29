alembic init -t async migration
alembic revision --autogenerate -m "msg" ----create a migration
alembic upgrade head ------apply themigration
