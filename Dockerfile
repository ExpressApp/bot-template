FROM python:3.11.5-alpine



# Install system-wide dependencies
RUN apk update && \
    apk add --no-cache --clean-protected git curl gcc python3-dev && \
    rm -rf /var/cache/apk/*

# Create user for app
ENV APP_USER=appuser
RUN adduser -D $APP_USER
WORKDIR /home/$APP_USER
USER $APP_USER

# Set python env vars
ENV PYTHONUNBUFFERED 1
ENV PYTHONNODEBUGRANGES 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONPATH="/home/$APP_USER:$PYTHONPATH"

# Use venv directly via PATH
ENV VENV_PATH=/home/$APP_USER/.venv/bin
ENV USER_PATH=/home/$APP_USER/.local/bin
ENV PATH="$VENV_PATH:$USER_PATH:$PATH"

# Set app env vars
ENV GUNICORN_CMD_ARGS ""

# Set build env vars
ARG CI_COMMIT_SHA=""
ENV GIT_COMMIT_SHA=${CI_COMMIT_SHA}

RUN pip install --user --no-cache-dir poetry==1.4.2 && \
    poetry config virtualenvs.in-project true

COPY poetry.lock pyproject.toml ./


RUN poetry install --only main


COPY alembic.ini .
COPY app app

EXPOSE 8000

CMD alembic upgrade head && \
    gunicorn "app.main:get_application()" --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0 $GUNICORN_CMD_ARGS
