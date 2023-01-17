# FOR ME: создать образ на основе базового слоя python (там будет ОС и интерпретатор Python)
FROM python:3.7-slim
# FOR ME: создать директорию (в контейнере) + сделать директорию /app <рабочей директорией>
WORKDIR /app/api_yamdb
# FOR ME: копировать (с локала) в <рабочую директорию /app >
COPY requirements.txt .
# FOR ME: выполнить <в контейнере>
RUN pip3 install -r ./requirements.txt --no-cache-dir
# FOR ME: копировать (с локала) директорию /api_yamdb в директорию /app
COPY . .
# FOR ME: запуск сервера <при старте контейнера>
CMD ["gunicorn", "api_yamdb.wsgi:application", "--bind", "0:8000" ] 