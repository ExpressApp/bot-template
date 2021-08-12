FROM python:3.9-slim

EXPOSE 8000

ENV PYTHONUNBUFFERED 1
ENV UVICORN_CMD_ARGS ""
ENV APP_USER=appuser

ARG CI_JOB_TOKEN=""
ARG GIT_HOST=""
ARG GIT_PASSWORD=${CI_JOB_TOKEN}
ARG GIT_LOGIN="gitlab-ci-token"


# Poetry can't read password to download private repos
RUN echo -e "machine ${GIT_HOST}\nlogin ${GIT_LOGIN}\npassword ${GIT_PASSWORD}" > ~/.netrc && \
    apt-get update && \
    apt-get install -y git sudo && \
    echo "${APP_USER} ALL = NOPASSWD: /usr/sbin/update-ca-certificates" > /etc/sudoers.d/update-ca-certificates && \
    rm -rf ~/.netrc && \
    apt-get clean autoclean && \
    apt-get autoremove --yes && \
    rm -rf /var/lib/{apt,dpkg,cache,log}/


RUN useradd --create-home $APP_USER
WORKDIR /home/$APP_USER
USER $APP_USER

CMD update-ca-certificates

ENV VENV_PATH=/home/$APP_USER/.venv/bin
ENV USER_PATH=/home/$APP_USER/.local/bin
ENV PATH="$VENV_PATH:$USER_PATH:$PATH"

COPY poetry.lock pyproject.toml ./

RUN pip install --user --no-cache-dir poetry==1.1.6 && \
    poetry config virtualenvs.in-project false && \
    poetry install --no-dev && \
    rm -rf ~/.cache/pypoetry

COPY alembic.ini .
COPY app app

ARG CI_COMMIT_SHA=""
ENV GIT_COMMIT_SHA=${CI_COMMIT_SHA}

CMD alembic upgrade head && \
    uvicorn --host=0.0.0.0 $UVICORN_CMD_ARGS app.main:app