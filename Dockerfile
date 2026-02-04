# Используем стабильную версию образа
FROM runpod/worker-comfyui:5.6.0

WORKDIR /
COPY . .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Команда запуска (используем стандартный старт-скрипт образа)
CMD ["/start.sh"]
