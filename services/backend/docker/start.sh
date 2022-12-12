#!/bin/bash

cd /app/src

python manage.py makemigrations
python manage.py migrate --fake-initial
exec python manage.py runserver 0.0.0.0:8000