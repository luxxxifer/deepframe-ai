FROM runpod/ai-worker-comfyui:latest
WORKDIR /
COPY . .
# Устанавливаем зависимости, если они есть в requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
# Запускаем оригинальный старт-скрипт образа, чтобы ComfyUI поднялся
CMD ["/start.sh"]
