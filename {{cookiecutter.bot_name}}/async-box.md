# async-box


## Структура шаблона

```
.
├── app
│   ├── api        - реализация роутов для приложения, включая необходимые для бота
│   ├── bot        - всё, что связано с обработкой команд пользователя
│   ├── db         - модели, функции для работы с БД и миграции
│   ├── resources  - текстовые или файловые ресурсы бота
│   ├── schemas    - схемы для (де)сериализации и валидации данных
│   ├── services   - сервисы с бизнес-логикой
│   ├── settings   - настройки env, логгера и запуска/остановки бота
│   └── main.py    - запуск сервера с инициализацией необходимых сервисов
├── scripts        - скрипты для запуска тестов, форматеров, линтеров
├── tests          - тесты, структура которых соответствует структуре проекта
└── pyproject.toml - конфигурация проекта с зависимостями
```

## Начало работы

1. Установите зависимости с помощью [poetry](https://python-poetry.org/docs/):

```bash
$ poetry install
```

Если `poetry` зависает, скорее всего вы пытаетесь скачать зависимости из приватных
репозиториев. Чтобы `poetry` получил доступ к ним, создайте файл `~/.netrc` и заполните
его необходимыми данными.

```netrc
machine company.vcs.host
login login
password password
```

**Примечание:** Если вы используете двухфакторную авторизацию, вместо пароля нужно
указать токен

2. Определите переменные окружения в файле `.env`. Пример см. в `example.env`.

3. Создайте новые команды используя [pybotx](https://github.com/ExpressApp/pybotx). Все
   команды бота находятся `app.bot.commands` и группируются в отдельные модули в
   зависимости от их логики. Тексты выносятся в `resources.strings`.

4. Импортируйте коллекторы команд в `app.bot.bot` и подключите их к боту.

5. Запустите БД и Redis в фоне через [docker-compose](https://docs.docker.com/compose/):

```bash
$ docker-compose -f docker-compose.dev.yml up -d
```

6. Примените миграции для инициализации БД с помощью
   [alembic](https://alembic.sqlalchemy.org/en/latest/tutorial.html):

```bash
$ poetry run alembic upgrade head

```

7. Запустите бота как приложение [FastAPI](https://fastapi.tiangolo.com/tutorial/) 
   через [uvicorn](https://fastapi.tiangolo.com/tutorial/).
   Флаг `--reload` используется только при разработке.

```bash
$ poetry run uvicorn app.main:app --reload
```

8. Для запуска автоформатировщиков (
[autoflake](https://github.com/myint/autoflake),
[isort](https://github.com/timothycrosley/isort),
[black](https://github.com/psf/black)
) используйте команду:

```bash
$ poetry run ./scripts/format
```

9. Для запуска линтеров (
[black](https://github.com/psf/black),
[isort](https://github.com/timothycrosley/isort),
[mypy](https://github.com/python/mypy),
[wemake-python-styleguide](https://github.com/wemake-services/wemake-python-styleguide)
) используйте команду:

```bash
$ poetry run ./scripts/lint
```

10. Для запуска тестов (
[pytest](https://docs.pytest.org/en/latest/),
[pytest-asyncio](https://github.com/pytest-dev/pytest-asyncio),
[pytest-env](https://github.com/MobileDynasty/pytest-env)
) используйте команду:

```bash
$ poetry run ./scripts/test
```
