FROM python:3.9

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /backend

COPY ./backend .
RUN pip install -r /backend/requirements/dev.txt
COPY ./docker/django/entrypoint.sh .
COPY ./docker/django/wait-for-postgres.sh .

ENTRYPOINT ["sh", "/backend/entrypoint.sh"]

EXPOSE 8080