## 0.13.0 (Jul 1, 2021)

### Changed

* **Breaking change:** `BotAccount` in settings replaced with `BotXCredentials` 
  (already have all nessessary fields).

* **Breaking change:** `search_user_on_each_cts` argument `List[BotAccount]` 
  changed to `List[BotXCredentials]`, which you can get from `bot.bot_accounts`.

* **Breaking change:** now only the necessary files, such as `poetry.lock`, `pyproject.toml`, `alembic.ini` and directory `app`, will copy to the docker image

* `poetry` dependency was updated to 1.1.6
