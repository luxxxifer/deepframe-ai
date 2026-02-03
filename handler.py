import runpod
import requests
import json
import time
import os

# Настройки адреса ComfyUI
COMFY_URL = "http://127.0.0.1:8188"

def handler(job):
    # 1. Получаем входные данные из запроса API
    job_input = job['input']
    # По умолчанию используем промпт из запроса, если его нет - стандартную фразу
    user_prompt = job_input.get("prompt", "nude elf woman in forest")
    
    # 2. Загружаем ваш воркфлоу
    try:
        with open('workflow_api.json', 'r') as f:
            workflow = json.load(f)
    except Exception as e:
        return {"error": f"Failed to load workflow_api.json: {str(e)}"}

    # 3. Модифицируем воркфлоу под запрос пользователя
    # Согласно вашему JSON, узел "197" содержит текст "PROMT HERE"
    if "197" in workflow:
        workflow["197"]["inputs"]["value"] = user_prompt
    
    # Дополнительно: если вы хотите менять Seed через API
    if "70" in workflow and "seed" in job_input:
        workflow["70"]["inputs"]["value"] = job_input["seed"]

    # 4. Отправляем запрос в ComfyUI
    payload = {
        "prompt": workflow,
        "client_id": "runpod_api"
    }
    
    try:
        # Отправляем задачу в очередь
        response = requests.post(f"{COMFY_URL}/prompt", json=payload)
        response.raise_for_status()
        prompt_id = response.json().get('prompt_id')
        
        # 5. Ожидание завершения (простой цикл опроса)
        # В идеале здесь должна быть проверка через WebSocket, но для начала хватит и этого
        while True:
            history_resp = requests.get(f"{COMFY_URL}/history/{prompt_id}")
            history = history_resp.json()
            
            if prompt_id in history:
                # Генерация завершена
                break
            time.sleep(1)
            
        return {
            "status": "success",
            "message": "Image generated",
            "prompt_id": prompt_id
        }
        
    except Exception as e:
        return {"error": f"Execution failed: {str(e)}"}

# Запуск обработчика RunPod
runpod.serverless.start({"handler": handler})
