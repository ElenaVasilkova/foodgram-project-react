# Проект Foodgram - продуктовый помощник

## Описание

Проект "Foodgram" предназначен для публикации рецептов приготовления различных блюд. "Foodgram" создан в качестве выпускного проекта курса [Python-разработчик](https://practicum.yandex.ru/backend-developer/) от [Яндекс.Практикум.](https://practicum.yandex.ru/)

На этом сервисе пользователи смогут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

## Технологии

- Python 3.10
- Django 3.2
- Django REST framework 3.14
- Nginx
- Docker
- Postgres 15

## Подготовка и запуск проекта
#### Запуск проекта в контейнерах

- Клонирование удаленного репозитория
```bash
git clone git@github.com:ElenaVasilkova/foodgram-project-react.git
cd infra
```
- В директории /infra создайте файл .env, с переменными окружения, по шаблону:
```
POSTGRES_USER=your_username
POSTGRES_PASSWORD=your_password
POSTGRES_DB=django_db

DB_HOST=db
DB_PORT=5432

SECRET_KEY='your_secret_key'
DEBUG=False
ALLOWED_HOSTS=127.0.0.1,localhost,server_ip,your_host
```
- Для работы с Workflow добавьте в Secrets GitHub переменные окружения, в репозитории проекта перейти в раздел settings/secrets/actions и создайте Actions secrets and variables по шаблону:
```
DB_HOST              db # название контейнера
DB_PORT              5432 # порт для подключения к БД 
HOST                 XXX.XXX.XXX.XXX # ip вашего сервера
USER                 your_username # Имя пользователя для подключения к серверу
SSH_KEY              # Приватный ключ доступа для подключению к серверу
PASSPHRASE           # Серкретный пароль, если ваш ssh-ключ защищён паролем
TELEGRAM_TO          # id Telegram-чата куда бот будет отправлять результат успешного выполнения
TELEGRAM_TOKEN       # Токен бота Telegram для отправки уведомления
DOCKER_USERNAME      # Имя пользователя Docker для публикации образов
DOCKER_PASSWORD      # Пароль пользователя Docker
```
- На сервере соберите docker-compose:
```bash
docker-compose up -d --build
```
- Выполните миграции, соберите статические файлы, создайте суперпользователя
```bash
docker-compose exec backend python manage.py migrate
```
```bash
docker-compose exec backend python manage.py collectstatic --no-input
```
```bash
docker-compose exec backend python manage.py createsuperuser
```
- Наполните базу данных ингредиентами и тегами
```bash
docker-compose exec backend python manage.py load_ingredients
```
```bash
docker-compose exec backend python manage.py load_tags
```

- Стандартная админ-панель Django доступна по адресу [`https://localhost/admin/`](https://localhost/admin/)
- Документация к проекту доступна по адресу [`https://localhost/api/docs/`](`https://localhost/api/docs/`)

---

#### Запуск API проекта в dev-режиме

- Клонирование удаленного репозитория (см. выше)
- Создание виртуального окружения и установка зависимостей
```bash
cd backend
python -m venv venv
. venv/bin/activate
pip install --upgade pip
pip install -r -requirements.txt
```
- Примените миграции и соберите статику
```bash
python manage.py migrate
python manage.py collectstatic --noinput
```
- Наполнение базы данных ингредиентами
```bash
python manage.py load_ingredients
```

- Запуск сервера
```bash
python manage.py runserver
```

---

## Об авторе

Василькова Елена Алексеевна   
Telegram: @Vasilkova_Elena_A
