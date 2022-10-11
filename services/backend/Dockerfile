FROM python:3.10-bullseye

WORKDIR /backend

RUN apt-get update && apt-get install libgeos-dev build-essential cmake -y

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

ADD ./requirements.txt /backend/requirements.txt
RUN pip install -r /backend/requirements.txt

COPY ./scripts ./src /backend

ENTRYPOINT ["sh", "/backend/entrypoint.sh"]

EXPOSE 8080