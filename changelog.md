## 0.13.0 (Jul 1, 2021)

### Changed

* **Breaking change:** `BotAccount` in settings replaced with `BotXCredentials` 
  (already have all nessessary fields).

* **Breaking change:** `search_user_on_each_cts` argument `List[BotAccount]` 
  changed to `List[BotXCredentials]`, which you can get from `bot.bot_accounts`.
