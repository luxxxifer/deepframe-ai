# Используем стабильную версию образа
FROM timpietruskyblibla/runpod-worker-comfy:3.4.0-base

WORKDIR /
COPY . .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Команда запуска (используем стандартный старт-скрипт образа)
CMD ["/start.sh"]
