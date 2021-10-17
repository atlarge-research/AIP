#!/bin/sh
cd /backend
chmod +x /backend/wait-for-postgres.sh
/backend/wait-for-postgres.sh db:5432 --timeout=0
python manage.py makemigrations
python manage.py migrate --fake-initial
python manage.py runserver 0.0.0.0:8080