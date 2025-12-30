alembic init -t async migration
--import the models in env.py
alembic revision --autogenerate -m "msg" ----create a migration
alembic upgrade head ------apply themigration
