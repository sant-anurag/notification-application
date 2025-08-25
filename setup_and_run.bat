@echo off
REM Create virtual environment
python -m venv .env

REM Activate virtual environment
call .env\Scripts\activate.bat

REM Upgrade pip
python -m pip install --upgrade pip

REM Install requirements
pip install -r requirements.txt

REM Run migrations
python manage.py migrate

REM Run server
python manage.py runserver
