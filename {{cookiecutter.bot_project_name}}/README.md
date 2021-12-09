# {{cookiecutter.bot_project_name}}

[![codecov](https://codecov.io/gh/ExpressApp/todo-bot/branch/master/graph/badge.svg?token=PTRJR2ITHW)](https://codecov.io/gh/ExpressApp/todo-bot)

Бот создан на базе шаблона [async-box](https://github.com/ExpressApp/async-box).

## Описание

{{cookiecutter.bot_short_description}}

## Инструкция по развёртыванию {{cookiecutter.bot_project_name}}

**NOTE**: *Если вы планируете развёртывать несколько ботов на сервере, используйте
продвинутый вариант инструкции: [advanced-deploy.md](advanced-deploy.md).*

1. Воспользуйтесь инструкцией [Руководство 
   администратора](https://express.ms/admin_guide.pdf) `-> Эксплуатация корпоративного 
   сервера -> Управление контактами -> Чат-боты`, чтобы создать бота в админке 
   eXpress. 
   Получите `secret_key` и `bot_id` кликнув на имя созданного бота. 
   Получите `cts_host` в строке браузера, когда вы в админке. 
   

2. Скачайте репозиторий на сервер:

```bash
git clone <THIS_REPOSITORY> /opt/express/bots/{{cookiecutter.bot_project_name}}
cd /opt/express/bots/{{cookiecutter.bot_project_name}}
```

3. Отредактируйте `docker-compose.yml` подставив вместо `cts_host`, `secret_key` и `bot_id` реальные значения.


4. Запустите контейнеры командой:

```bash
docker-compose up -d
```

5. Убедитесь, что в логах нет ошибок.

```bash
docker-compose logs
```

6. Найдите бота через поиск корпоративных контактов (иконка человечка слева-сверху в
   мессенджере), напишите ему что-нибудь для проверки.
