# Используем стабильную версию образа
FROM runpod/ai-worker-comfyui:1.1.2

WORKDIR /
COPY . .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Команда запуска (используем стандартный старт-скрипт образа)
CMD ["/start.sh"]
