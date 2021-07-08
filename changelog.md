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
