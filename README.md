[![Typing SVG](https://readme-typing-svg.herokuapp.com?font=Fira+Code&size=30&pause=1000&color=F71329&multiline=true&width=435&lines=+yamdb_final)](https://git.io/typing-svg)  
[![Typing SVG](https://readme-typing-svg.herokuapp.com?font=Fira+Code&size=20&pause=1000&color=1D39F7&multiline=true&width=435&lines=+yamdb_final)](https://git.io/typing-svg)  
[![Typing SVG](https://readme-typing-svg.herokuapp.com?font=Fira+Code&size=15&duration=2000&pause=1000&color=1FBB30F6&multiline=true&width=435&lines=+yamdb_final)](https://git.io/typing-svg)    
[![Typing SVG](https://img.shields.io/badge/yamdb_final-sprint--13%20ver.2-green)](https://git.io/typing-svg)
![example workflow](https://github.com/Celin-zsv/yamdb_final/actions/workflows/yamdb_workflow.yml/badge.svg?event=push)
### Проект спринта-13, ver.2, Зеленковский Сергей  
![](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![](https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=green)
![](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)
![](https://img.shields.io/badge/DJANGO-REST-ff1709?style=for-the-badge&logo=django&logoColor=white&color=ff1709&labelColor=gray)
![](https://img.shields.io/badge/JWT-000000?style=for-the-badge&logo=JSON%20web%20tokens&logoColor=white)
![](https://img.shields.io/badge/Nginx-009639?style=for-the-badge&logo=nginx&logoColor=white)
![](https://img.shields.io/badge/Docker-2CA5E0?style=for-the-badge&logo=docker&logoColor=white)
#### Содержание
1. Описание проекта
2. Описание команд
3. Пример развернутого проекта http://158.160.38.1/api/v1/
***
1. *Описание проекта yamdb_final*
## CI & CD api_yamdb
Continuous Integration & Continuous Deployment проекта api_yamdb
  * workflow:  
    * тесты
    * обновление образов на Docker Hub
    * деплой на удаленной виртуальной машине
    * уведомление в Telegram
  * событие: git push
  * api_yamdb: https://github.com/Celin-zsv/api_yamdb-1

Parameter  | Value
-------------|:-------------
Наименование проекта  | yamdb_final: CI & CD проекта api_yamdb
Назначение проекта | автоматически развернуть проект <на удаленной виртуальной машине>
Tech Stack. Client. APP | Docker version 20.10.12 , docker-compose version 1.29.2 (and higher)
Tech Stack. Client. OS | Windows (+установлен wsl) , Linux, MacOS
DockerHub  | [https://hub.docker.com/repository/docker/zelenkovskii/yamdb_final/general](https://hub.docker.com/repository/docker/zelenkovskii/yamdb_final/general)
Author | Sergei Zelenkovskii, svzelenkovskii@gmail.com  

2. *Описание команд*  

2.1. Локальная машина:
* клонировать репозиторий:
[https://github.com/Celin-zsv/yamdb_final](https://github.com/Celin-zsv/yamdb_final)
* доработать  /заменить app: ``` yamdb_final/api_yamdb/ ```
* доработать config flake8: ``` yamdb_final/setup.cfg ```
* доработать doc: ```yamdb_final/api_yamdb/static/redoc.yaml```
* not optional: руками загрузить образ на DockerHub (после доработки app):
  * установить Docker: https://www.docker.com/products/docker-desktop
  * создать образ: ``` docker build -t <username/imagename:tag> .```
  * подключиться к hub.docker.com: ```docker login -u <login DockerHub>```
  * загрузить образ на DockerHub:``` docker push <username/imagename:tag> ```
* доработать workflow: ```yamdb_final/.github/workflows/yamdb_workflow.yml```
  * job 1:
    * set up Python
    * install dependencies and flake8
    * test with flake8 and django tests
  * job 2:
    * build image (from context local dir)
    * push image to DockerHub
      * указать dir app: ```context: ./api_yamdb/```
  * job 3:
    * pull image (from DockerHub)
    * deploy containers (on remote virtual host):
      * подключиться через SSH_KEY (на основе GitHub Actions Secrets)
      * stop docker
      * delete container ```web```
      * создать и наполнить файл ```.env``` (на основе GitHub Actions Secrets)
      * запустить docker-compose: ``` sudo docker-compose up -d ```
  * job 4:
    * отправка уведомления в Telegram об успешном процессе деплоя
* доработать ```yamdb_final/infra/docker-compose.yaml```
  * инструкции для контейнеров: ``` web, db, nginx ```
    * тома данных ``` volumes ``` для: бд, статики, медиа (files loaded by users)
    * образы ``` image ```, в т.ч. контейнер web использует загруженный с DockerHub образ
    * зависимости ``` depends_on ```
    * порты nginx: проксирования запросов <с внеш. 80> <на внутр. 80>  
    * директории для <копирования при сборке>
* доработать ```yamdb_final/api_yamdb/Dockerfile```
    * запуск ``` Dockerfile ``` -> в результате в контейнере ```web```:
      * установить : ОС, интерпретатор Python
      * создать + сделать рабочей dir: ```WORKDIR /app```
      * копировать (с локала) в ```/app```: ```requirements.txt```
      * установить зависимости: ```RUN pip3 install -r ./requirements.txt --no-cache-dir```
      * копировать (с локала) директорию ```/api_yamdb``` в директорию ```/app```
      * запустить сервер ```gunicorn```: ```CMD ["gunicorn", "api_yamdb.wsgi:application", "--bind", "0:8000" ]```
      * развернётся проект, запущенный через Gunicorn с базой данных Postgres
* редактировать ```nginx/default.conf```:
  * изменить ``` server_name <IP удаленной виртуальной машины> ```
  * дополнить ``` location / ``` :
```
    location / {
  proxy_set_header Host $host;
  proxy_set_header X-Real-IP $remote_addr;
  proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
  proxy_set_header X-Forwarded-Proto $scheme;
  proxy_pass http://web:8000;
  }
```

2.2. Удаленная виртуальная машина:
* скопировать docker-compose.yaml:
  * из (локально): ```yamdb_final/infra/docker-compose.yaml```
  * на (удаленно): ```home/<username>/docker-compose.yaml```
* скопировать default.conf (nginx):
  * из (локально): ```yamdb_final/infra/nginx/default.conf```
  * на (удаленно): ```home/<username>/nginx/default.conf```  
* остановить nginx: ``` sudo systemctl stop nginx ```
* установить docker: ``` sudo apt install docker.io ```
* установить docker-compose: https://docs.docker.com/compose/install/linux/#install-the-plugin-manually
* выполнить миграции в контейнере ```web```: ``` docker-compose exec web python manage.py migrate ```
* собрать статику в ```web```: ``` docker-compose exec web python manage.py collectstatic --no-input ```
* создать суперпользователя в ```web```: ``` docker-compose exec web python manage.py createsuperuser ```

2.3. GitHub:
* Добавить в GitHub Actions Secrets переменные окружения: ``` HOST, USER, SSH_KEY, PASSPHRASE, DB_ENGINE, DB_NAME, POSTGRES_USER, POSTGRES_PASSWORD, DB_HOST, DB_PORT ```   


3. *Пример развернутого проекта на удаленной виртуальной машине*  
http://158.160.38.1/api/v1/ - REST API  
http://158.160.38.1/admin/  - админ панель  
http://158.160.38.1/redoc/  - документация

@zsv
