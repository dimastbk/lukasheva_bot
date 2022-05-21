FROM python:3.10-slim

# PROJECT_ROOT - путь до каталога внутри контейнера, в который будет
# копироваться приложение
ENV PROJECT_ROOT=/app

# Путь до исходников
ENV PYTHONPATH=$PYTHONPATH:$PROJECT_ROOT

COPY requirements.txt $PROJECT_ROOT/

WORKDIR $PROJECT_ROOT

# Запускаем установку зависимостей одной командой, чтобы облегчить образ
RUN set -ex && \
    # Установка зависимостей
    pip install --disable-pip-version-check -r requirements.txt

COPY ./ $PROJECT_ROOT

CMD ["python", "main.py"]
