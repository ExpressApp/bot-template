FROM python:3.9-slim

ENV PYTHONUNBUFFERED 1
ENV UVICORN_CMD_ARGS ""

EXPOSE 8000

ENV APP_USER=appuser
RUN useradd --create-home $APP_USER

RUN apt-get update && \
    apt-get install -y sudo git curl && \
    echo "${APP_USER} ALL = NOPASSWD: /usr/sbin/update-ca-certificates" > /etc/sudoers.d/express_bot && \
    apt-get clean autoclean && \
    apt-get autoremove --yes && \
    rm -rf /var/lib/{apt,dpkg,cache,log}/

ENV VENV_PATH=/home/$APP_USER/.venv/bin
ENV USER_PATH=/home/$APP_USER/.local/bin
ENV PATH="$VENV_PATH:$USER_PATH:$PATH"

WORKDIR /home/$APP_USER
USER $APP_USER

COPY poetry.lock pyproject.toml ./

RUN pip install --user --no-cache-dir poetry==1.1.6 && \
  poetry config virtualenvs.in-project true

{% if cookiecutter.is_private_dependencies == "False"  %}
RUN poetry install --no-dev && \
    rm -rf ~/.cache/pypoetry
{% else %}
ARG CI_JOB_TOKEN=""
ARG GIT_HOST=""
ARG GIT_PASSWORD=${CI_JOB_TOKEN}
ARG GIT_LOGIN="gitlab-ci-token"
# Poetry can't read password to download private repos
RUN echo -e "machine ${GIT_HOST}\nlogin ${GIT_LOGIN}\npassword ${GIT_PASSWORD}" > ~/.netrc && \
    poetry install --no-dev && \
    rm -rf ~/.cache/pypoetry && \
    rm -rf ~/.netrc
{% endif %}

COPY alembic.ini .
COPY app app

ARG CI_COMMIT_SHA=""
ENV GIT_COMMIT_SHA=${CI_COMMIT_SHA}

CMD sudo update-ca-certificates && \
    alembic upgrade head && \
    uvicorn --host=0.0.0.0 $UVICORN_CMD_ARGS app.main:app
