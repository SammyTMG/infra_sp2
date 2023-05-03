# API YaMDb

API для сервиса YamDb - хранение и сбор отзывов о фильмах, книгах или музыке.

## Описание

Проект YaMDb собирает рецензии пользователей на произведения. Произведения делятся на категории: «Книги», «Фильмы», «Музыка». Зарегистрированные пользователи могут оставить к произведениям текстовые отзывы и поставить произведению оценку в диапазоне от одного до десяти, из пользовательских оценок формируется рейтинг произведения. 

### Использовалось

Python 3.7, Django, DRF, Simple-JWT, PostgreSQL, Docker, nginx, gunicorn.

### Как запустить

Клонируем репозиторий и переходим в него:
```
git clone git@github.com:SammyTMG/infra_sp2.git
cd infra_sp2
cd api_yamdb
```

Создаем и активируем виртуальное окружение:
```
python3 -m venv venv
source /venv/bin/activate (source /venv/Scripts/activate - для Windows)
python -m pip install --upgrade pip
```

Ставим зависимости из requirements.txt:
```
pip install -r requirements.txt
```

Переходим в папку с файлом docker-compose.yaml:
```
cd infra
```

Поднимаем контейнеры (infra_db_1, infra_web_1, infra_nginx_1):
```
docker-compose up -d --build
```

Выполняем миграции:
```
docker-compose exec web python manage.py makemigrations users
docker-compose exec web python manage.py makemigrations reviews
docker-compose exec web python manage.py migrate
```

Создаем суперпользователя:
```
docker-compose exec web python manage.py createsuperuser
```

Србираем статику:
```
docker-compose exec web python manage.py collectstatic --no-input
```

Создаем дамп базы данных (нет в текущем репозитории):
```
docker-compose exec web python manage.py dumpdata > dumpPostrgeSQL.json
```

Останавливаем контейнеры:
```
docker-compose down -v
```

Пример содержимого файла .env,  расположенного по пути infra/.env:
```
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432
```

### Документация API YaMDb

Документация доступна по эндпойнту: http://localhost/redoc/
