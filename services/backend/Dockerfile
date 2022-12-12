###############################################
# Base Image
###############################################
FROM python:3.10-slim-bullseye as python-base

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_VERSION=1.2.2 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1 \
    PYSETUP_PATH="/app" \
    VENV_PATH="/app/.venv"

ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"

COPY ./docker/start.sh /start.sh
RUN chmod +x /start.sh

COPY ./docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

COPY ./docker/wait-for-postgres.sh /wait-for-postgres.sh
RUN chmod +x /wait-for-postgres.sh

WORKDIR $PYSETUP_PATH

EXPOSE 8000
ENTRYPOINT [ "/entrypoint.sh" ]

###############################################
# Builder Image
###############################################
FROM python-base as builder-base

RUN apt-get update && \
    apt-get install --no-install-recommends -y \
        build-essential \
        cmake 

RUN pip install poetry==$POETRY_VERSION

WORKDIR $PYSETUP_PATH
COPY ./poetry.lock ./pyproject.toml ./

RUN poetry install --without dev


###############################################
# Development Image
###############################################
FROM python-base as development

COPY --from=builder-base $PYSETUP_PATH $PYSETUP_PATH
COPY src $PYSETUP_PATH/src
CMD [ "/start.sh" ]


###############################################
# Production Image
###############################################
FROM python-base as production

RUN addgroup --gid 1001 --system app && \
    adduser --no-create-home --shell /bin/false --disabled-password --uid 1001 --system --group app

USER app

COPY --chown=app:app --from=builder-base $PYSETUP_PATH $PYSETUP_PATH
COPY --chown=app:app src $PYSETUP_PATH/src

COPY --chown=app:app ./docker/gunicorn_conf.py /gunicorn_conf.py

WORKDIR $PYSETUP_PATH/src

CMD [ "gunicorn", "--config", "/gunicorn_conf.py", "config.wsgi"]