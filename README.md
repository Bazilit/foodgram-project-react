## ***Foodgram, «Продуктовый помощник»***
![yamdb workflow](https://github.com/Bazilit/foodgram-project-react/actions/workflows/main.yml/badge.svg)

---
### Описание:
Сервис позволяет пользователю публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», 
а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.

---
### Проект развернут по адресу:

[Сайт](http://51.250.30.28)

Данные админа:
login: admin
password: admin
---

### Стэк технологий:
[![Python](https://img.shields.io/badge/-Python-464646?style=flat-square&logo=Python)](https://www.python.org/)
[![Django](https://img.shields.io/badge/-Django-464646?style=flat-square&logo=Django)](https://www.djangoproject.com/)
[![Django REST Framework](https://img.shields.io/badge/-Django%20REST%20Framework-464646?style=flat-square&logo=Django%20REST%20Framework)](https://www.django-rest-framework.org/)
[![PostgreSQL](https://img.shields.io/badge/-PostgreSQL-464646?style=flat-square&logo=PostgreSQL)](https://www.postgresql.org/)
[![Nginx](https://img.shields.io/badge/-NGINX-464646?style=flat-square&logo=NGINX)](https://nginx.org/ru/)
[![gunicorn](https://img.shields.io/badge/-gunicorn-464646?style=flat-square&logo=gunicorn)](https://gunicorn.org/)
[![docker](https://img.shields.io/badge/-Docker-464646?style=flat-square&logo=docker)](https://www.docker.com/)
[![Yandex.Cloud](https://img.shields.io/badge/-Yandex.Cloud-464646?style=flat-square&logo=Yandex.Cloud)](https://cloud.yandex.ru/)
---

## Инструкция по запуску проекта на удаленном сервере:
#### 1. Подключиться и авторизоваться на удаленном сервере:
```
ssh <имя_сервера>@<публичный_ip_сервера>
```
#### 2. Установите docker и docker-compose:
* Установка docker:
```
sudo apt install docker.io
```
* Установка docker-compose:
```
sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```
#### 3. Найстройка nginx.conf и docker-compose.yml:
* Отредактируйте файл infra/nginx.conf и в строке server_name замените IP по умолчанию на свой IP
* Скопируйте файлы docker-compose.yml и nginx.conf из директории infra на в директорию /home/<username>
```
sudo cp docker-compose.yml /home/<username>/
sudo cp nginx.conf /home/<username>/
```
* Если проект находится на локальной машине. Скопируйте из директории infra файлы docker-compose.yml и nginx.conf и отправьте их на сервер:
```
scp docker-compose.yml <username>@<host>:/home/<username>/docker-compose.yml
scp nginx.conf <username>@<host>:/home/<username>/nginx.conf
```
#### 3.1 Дополнительно. Создание .env файла для локального запуска:
* Важно! Если решите запустить проект локально, для работы и запуска потребуется .env файл.
* Внутри самого проекта. В папке backend/foodgram/ на уровне файла settings.py
* Создайте файл .env:
```
sudo touch .env
```
* Откройте файл .env:
```
sudo nano .env
```
* заполните файл соответствующими данными:
```
    SECRET_KEY=<секретный ключ проекта django>
    DB_ENGINE=<django.db.backends.postgresql>
    DB_NAME=<имя базы данных postgres>
    DB_USER=<пользователь бд>
    DB_PASSWORD=<пароль>
    DB_HOST=<db>
    DB_PORT=<5432>
```
* Примечание! При автоматическом deploy и развертывание проекта на сервере, данный файл создается автоматически.
#### 4. Подготовка и запуск Workflow:
* Для работы с Workflow добавьте в Secrets GitHub переменные окружения для работы:
```
    DB_ENGINE=<django.db.backends.postgresql>
    DB_NAME=<имя базы данных postgres>
    DB_USER=<пользователь бд>
    DB_PASSWORD=<пароль>
    DB_HOST=<db>
    DB_PORT=<5432>
    DOCKER_PASSWORD=<пароль от DockerHub>
    DOCKER_USERNAME=<имя пользователя>
    SECRET_KEY=<секретный ключ проекта django>
    USER=<username для подключения к серверу>
    HOST=<IP сервера>
    PASSPHRASE=<пароль для сервера, если он установлен>
    SSH_KEY=<ваш SSH ключ (для получения команда: cat ~/.ssh/id_rsa)>
    TELEGRAM_TO=<ID чата, в который придет сообщение>
    TELEGRAM_TOKEN=<токен вашего бота>
```
* Workflow состоит из трёх шагов:
  - Проверка кода на соответствие требованиям PEP8;
  - Сборка и публикация образа на DockerHub;
  - Автоматический деплой на удаленный сервер;
  - Отправка уведомления в телеграм-чат;

#### 5. Сборка образа и запуск docker-compose:
* Для ручного запуска проекта.
  По пути foodgram-project-react/infra запустите docker-compose:
```
sudo docker-compose up -d --build
```
  Где:
    -d - запуск в фоновом режиме
    --build - пересборка контайнеров
* Если запуск происходит после Workflow, docker-compose запустится автоматически.
* После запуска docker-compose обязательно проверьте статус контейнеров. Запущенный контейнер отображается со статусом "UP".
  Проверить можно с помощью команды:
```
sudo docker container ls
```
* Если контейнер не запустился. Ознакомиться с логами запуска можно с помощью команды:
```
sudo docker container logs <id_контейнера>
```  
#### 6. Создание таблиц БД и сбор файлов статики:
* Подготовка к миграциям внутри контейнера:
```
sudo docker-compose exec backend python manage.py makemigrations --noinput
```
* Запуск миграций внутри контейнера:
```
sudo docker-compose exec backend python manage.py migrate --noinput
```
* Сбор файлов статики внутри контейнера:
```
sudo docker-compose exec backend python manage.py collectstatic --noinput
```
* Создайте суперпользователя с правами администратора:
```
sudo docker-compose exec backend python manage.py createsuperuser
```
---
#### Автор: *Шарковский А.* *https://github.com/Bazilit*
---
