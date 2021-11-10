#!/bin/sh

cd /backend

chmod +x /backend/wait-for-postgres.sh
/backend/wait-for-postgres.sh db:5432 --timeout=0

python src/manage.py makemigrations
python src/manage.py migrate 
python src/manage.py runserver 0.0.0.0:8080 --settings=config.settings.local