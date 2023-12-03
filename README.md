# Foodgram - продуктовый помощник

https://github.com/InAnotherLife/foodgram

https://t.me/JohnWooooo

[![Foodgram workflow](https://github.com/InAnotherLife/foodgram/actions/workflows/main.yml/badge.svg)](https://github.com/InAnotherLife/foodgram/actions/workflows/main.yml)

***

## О проекте

Foodgram - это сервис, позволяющий делиться своими кулинарными шедеврами. Здесь Вы можете создавать и публиковать свои рецепты, а также находить вдохновение в рецептах других пользователей.

***

## Технологии
* Django 4.2
* Django REST framework 3.14
* Python 3.10

***

## 1. Инструкция по развертыванию проекта на локальном сервере
1. Клонировать репозиторий и перейти в папку с проектом:
```
git clone git@github.com:InAnotherLife/foodgram.git
```

2. Создать файл .env с переменными окружения.\
Сгенерировать секретный ключ и сохранить в переменной SECRET_KEY.\
SU_NAME, SU_EMAIL, SU_PASSWORD - данные суперпользователя.

Пример заполнения файла .env:
```
SECRET_KEY='KEY'
DEBUG=True # True отладка включена, False отладка отключена
DATABASE=Prod # Prod для PostgreSQL, Dev для SQLite3
POSTGRES_DB=django_db
POSTGRES_USER=django_user
POSTGRES_PASSWORD=django_password
DB_HOST=db
DB_PORT=5432
ALLOWED_HOSTS=127.0.0.1;localhost
CSRF_TRUSTED_ORIGINS=http://localhost
CORS_ALLOWED_ORIGINS=http://127.0.0.1;http://localhost
SU_NAME=admin
SU_EMAIL=admin@mail.ru
SU_PASSWORD=pass
```

3. Перейти в папку docker и запустить проект при помощи команды:
```
sudo docker compose -f docker-compose.local.yml up -d
```

4. Выполнить миграции в БД:
```
sudo docker compose -f docker-compose.local.yml exec backend python manage.py makemigrations
sudo docker compose -f docker-compose.local.yml exec backend python manage.py migrate
```

5. Собрать статику:
```
sudo docker compose -f docker-compose.local.yml exec backend python manage.py collectstatic --no-input
```

6. Создать суперпользователя:
```
sudo docker compose -f docker-compose.local.yml exec backend python manage.py create_su
```

7. Для импорта данных в БД необходимо выполнить команду:
```
sudo docker compose -f docker-compose.local.yml exec backend python manage.py import_data
```

Проект доступен по адресу - http://localhost/  
API - http://localhost/api/  
Админка - http://localhost/admin/  
ReDoc - http://localhost/api/docs/

***

## 2. Инструкция по развертыванию проекта на удаленном сервере
1. Зайти на удаленный сервер и создать папку foodgram.

2. В папке foodgram создать файл .env с переменными окружения.\
Сгенерировать секретный ключ и сохранить в переменной SECRET_KEY.\
В переменные ALLOWED_HOSTS и CORS_ALLOWED_ORIGINS записать IP-адрес сервера и доменное имя сайта.\
В переменную CSRF_TRUSTED_ORIGINS записать доменное имя сайта.\
SU_NAME, SU_EMAIL, SU_PASSWORD - данные суперпользователя.

Пример заполнения файла .env:
```
SECRET_KEY='KEY'
DEBUG=False # True отладка включена, False отладка отключена
DATABASE=Prod # Prod для PostgreSQL, Dev для SQLite3
POSTGRES_DB=django_db
POSTGRES_USER=django_user
POSTGRES_PASSWORD=django_password
DB_HOST=db
DB_PORT=5432
ALLOWED_HOSTS=xxx.xxx.xxx.xxx;127.0.0.1;localhost;доменное_имя
CSRF_TRUSTED_ORIGINS=http://localhost;https://доменное_имя
CORS_ALLOWED_ORIGINS=https://xxx.xxx.xxx.xxx;http://127.0.0.1;http://localhost;https://доменное_имя
SU_NAME=admin
SU_EMAIL=admin@mail.ru
SU_PASSWORD=pass
```

3. В папку foodgram скопировать файлы docker-compose.yml и nginx.conf из папки docker проекта.

4. Открыть файл nginx.conf и в переменную server_name записать IP-адрес сервера и доменное имя сайта.

5. На удаленном сервере изменить файл конфигурации Nginx:
```
sudo nano /etc/nginx/sites-enabled/default
```

Для этого записать и сохранить новые настройки:
```
server {
    listen 80;
    server_tokens off;
    client_max_body_size 20M;
    server_name xxx.xxx.xxx.xxx доменное_имя;

    location / {
        proxy_set_header        Host $http_host;
        proxy_pass http://127.0.0.1:8000;
    }
}
```
В переменную server_name записать IP-адрес сервера и доменное имя сайта.

6. Проверить файл конфигурации Nginx:
```
sudo nginx -t
```

7. Перезагрузить Nginx:
```
sudo systemctl reload nginx
```

8. Перейти в папку foodgram и запустить проект при помощи команды:
```
sudo docker compose up -d
```

9. Выполнить миграции в БД:
```
sudo docker compose exec backend python manage.py makemigrations
sudo docker compose exec backend python manage.py migrate
```

10. Собрать статику:
```
sudo docker compose exec backend python manage.py collectstatic --no-input
```

11. Создать суперпользователя:
```
sudo docker compose exec backend python manage.py create_su
```

12. Для импорта данных в БД необходимо выполнить команду:
```
sudo docker compose exec backend python manage.py import_data
```

Проект доступен по адресу - http://доменное_имя/  
API - http://доменное_имя/api/  
Админка - http://доменное_имя/admin/  
ReDoc - http://доменное_имя/api/docs/
