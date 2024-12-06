FROM python:3.9-alpine 

# Устанавливаем рабочую директорию
WORKDIR /app

RUN apk add --no-cache \
    postgresql-dev \
    gcc \
    musl-dev

# Копируем файл зависимостей и устанавливаем их
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

# Копируем исходный код приложения
COPY . .

RUN chmod +x entrypoint.sh

# Открываем порт 5000 для Flask
EXPOSE 5000


# Команда для запуска приложения
#CMD [ "flask", "run", "--host=0.0.0.0", "--port=5000"]
ENTRYPOINT ["./entrypoint.sh"]