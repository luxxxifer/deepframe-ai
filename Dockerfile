# Используем стабильную версию образа
FROM timpietruskyblibla/runpod-worker-comfy:3.4.0-base

WORKDIR /

# --- УСТАНОВКА КАСТОМНЫХ НОД ---
# Клонируем репозитории напрямую в папку custom_nodes образа
# Устанавливаем git, создаем папку и клонируем ноды
RUN apt-get update && apt-get install -y git && \
    mkdir -p /comfyui/custom_nodes && \
    cd /comfyui/custom_nodes && \
    git clone https://github.com/pythongosssss/ComfyUI-Custom-Scripts.git && \
    git clone https://github.com/theUpsider/ComfyUI-Logic.git

# Устанавливаем зависимости для самих нод (если они есть)
RUN if [ -f /comfyui/custom_nodes/ComfyUI-Custom-Scripts/requirements.txt ]; then pip install -r /comfyui/custom_nodes/ComfyUI-Custom-Scripts/requirements.txt; fi

COPY . .

# Твои зависимости для бота
RUN pip install --no-cache-dir -r requirements.txt

CMD ["/start.sh"]
