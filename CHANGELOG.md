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
