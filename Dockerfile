# Используем стабильную версию образа
FROM runpod/ai-worker-comfyui:1.2.1

WORKDIR /
COPY . .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Команда запуска (используем стандартный старт-скрипт образа)
CMD ["/start.sh"]
