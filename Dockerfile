FROM python:3.6
WORKDIR /backend
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ADD ./backend/requirements.txt /backend/requirements.txt
RUN pip install -r /backend/requirements.txt
COPY ./backend .
COPY ./entrypoint.sh .
ENTRYPOINT ["sh", "/backend/entrypoint.sh"]
EXPOSE 8080
