FROM timpietruskyblibla/runpod-worker-comfy:3.4.0-base

WORKDIR /app

RUN apt-get update \
 && apt-get install -y --no-install-recommends git \
 && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /comfyui/custom_nodes \
 && cd /comfyui/custom_nodes \
 && [ -d "ComfyUI-Custom-Scripts" ] || git clone --depth 1 https://github.com/pythongosssss/ComfyUI-Custom-Scripts.git \
 && [ -d "ComfyUI-Logic" ] || git clone --depth 1 https://github.com/theUpsider/ComfyUI-Logic.git

RUN if [ -f /comfyui/custom_nodes/ComfyUI-Custom-Scripts/requirements.txt ]; then \
      pip install --no-cache-dir -r /comfyui/custom_nodes/ComfyUI-Custom-Scripts/requirements.txt; \
    fi

COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY . /app

CMD ["/start.sh"]
