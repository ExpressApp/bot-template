## 0.19.0 (Nov 14, 2021)

### Changed

* Changed the way sqlalchemy is used


## 0.18.0 (Sep 22, 2021)

### Added

* Add test to build image and run application.


## 0.17.0 (Sep 09, 2021)

### Changed

* **Breaking change:** Rename all environment and python variables containing a DSN for 
PostgreSQL database to `POSTGRES_DSN`
* Changed Dockerfile to install dependencies to user's home directory
* Changed docker-compose example config in README.md

## 0.16.5 (Sep 09, 2021)

### Changed

* Update `README.md`


## 0.16.4 (Sep 08, 2021)

### Added

* Add `pytest-env` dependency so that you can run pytest without passing environment variables.


## 0.16.3 (Aug 31, 2021)

### Added

* Logging for notification callbacks (BotX bot API v4 feature)

## 0.16.2 (Aug 26, 2021)

### Changed

* `botx` dependency was updated to 0.23.0.
* `bot.authorize` now is `startup_event`.


## 0.16.1 (Aug 23, 2021)

### Fixed

* A little error with sqlalchemy related to session

### Changed

* Restructured dockerfile

## 0.16.0 (Aug 16, 2021)

### Changed

* Rename CI/CD jobs `deploy.test` and `deploy.prod` to `deploy.botstest` and `deploy.botsprod`


## 0.15.9 (Aug 10, 2021)

### Changed

* Dockerfile uses venv to set up dependencies, run app.

  
## 0.15.8 (Aug 09, 2021)

### Fixed

* Fix an error in a migration test.

### Changed

* Replace variable `bot_name` with `bot_project_name`.
* Add `APP_ENV` to example.env 

  
## 0.15.7 (Aug 02, 2021)

### Removed

* Remove external cts user message. This dependency is no longer required
  as user access to the bot is now controlled in the cts admin panel.


## 0.15.6 (Jul 30, 2021)

### Fixed

* Remove unused linters rules.


## 0.15.5 (Jul 28, 2021)

### Added

* Add AsyncBox tutorial to `async-box.md`


## 0.15.4 (Jul 23, 2021)

### Fixed

* Now tests use `TestAppSettings` instead of environment variables.


## 0.15.3 (Jul 22, 2021)

### Fixed

* Bug with migrations fixture in tests

### Removed

* `databases` package removed from dependencies


## 0.15.2 (Jul 20, 2021)

### Added

* SQLAlchemy support and example model


## 0.15.1 (Jul 19, 2021)

### Added

* Tests to make a new project from cookiecutter template and run pytest in it


## 0.15.0 (Jul 14, 2021)

### Changed

* **Breaking change:** upgrade dependencies:
  *  Upgrade python from `3.8` to `3.9`
  *  Upgrade fastapi from `0.61.2` to `0.66.0`
  *  Upgrade uvicorn from `0.12.3` to `0.13.14`
  *  Upgrade tortoise-orm from `0.16.18` to `0.17.3`
  *  Upgrade databases from `0.4.1` to `0.4.3`
  *  Upgrade alembic from `1.3.2` to `1.6.5`
  *  Upgrade psycopg2-binary from `2.8.6` to `2.9.1`
  *  Upgrade mako from `1.1.0` to `1.1.4`


## 0.14.1 (Jul 9, 2021)

### Fixed

* Dependencies resolving (update pybotx-fsm version).


## 0.14.0 (Jul 7, 2021)

### Removed

* **Breaking change:** Remove models that stored all the information about users,
  chats and CTS. Previously, the BotX API did not provide the necessary functionality,
  and these models were the only way to work with Express data.
  Now they are no longer needed.


## 0.13.0 (Jul 1, 2021)

### Changed

* **Breaking change:** `BotAccount` in settings replaced with `BotXCredentials`
  (already have all nessessary fields).

* **Breaking change:** `search_user_on_each_cts` argument `List[BotAccount]`
  changed to `List[BotXCredentials]`, which you can get from `bot.bot_accounts`.

* **Breaking change:** now only the necessary files, such as `poetry.lock`, `pyproject.toml`, `alembic.ini` and directory `app`, will copy to the docker image

* `poetry` dependency was updated to 1.1.6
