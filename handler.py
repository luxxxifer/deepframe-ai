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
    # Получаем промпт от пользователя. Если его нет в запросе, берем заглушку.
    user_prompt = job_input.get("prompt", "elf woman in forest, masterpiece")
    
    # 2. Загружаем ваш воркфлоу
    try:
        with open('workflow_api.json', 'r') as f:
            workflow = json.load(f)
    except Exception as e:
        return {"error": f"Failed to load workflow_api.json: {str(e)}"}

    # 3. Модифицируем воркфлоу под ТВОЙ JSON
    # В твоем файле за промпт отвечает узел "27" (StringConcatenate)
    # Текст промпта вставляем в поле "string_b"
    if "27" in workflow:
        workflow["27"]["inputs"]["string_b"] = user_prompt
        print(f"Prompt set to node 27: {user_prompt}")
    else:
        return {"error": "Node 27 not found in workflow. Check your JSON file."}
    
    # Меняем Seed (узел 70), чтобы картинки каждый раз были разными
    if "70" in workflow:
        new_seed = job_input.get("seed", int(time.time()))
        workflow["70"]["inputs"]["value"] = new_seed
        print(f"Seed set to node 70: {new_seed}")

    # 4. Отправляем запрос в ComfyUI
    payload = {
        "prompt": workflow,
        "client_id": "runpod_api"
    }
    
    try:
        # Отправляем задачу в очередь ComfyUI
        response = requests.post(f"{COMFY_URL}/prompt", json=payload)
        response.raise_for_status()
        prompt_id = response.json().get('prompt_id')
        
        # 5. Ожидание завершения
        print(f"Job sent, prompt_id: {prompt_id}. Waiting for completion...")
        while True:
            history_resp = requests.get(f"{COMFY_URL}/history/{prompt_id}")
            history = history_resp.json()
            
            if prompt_id in history:
                # Генерация завершена!
                break
            time.sleep(1)
            
        return {
            "status": "success",
            "message": "Image generated successfully",
            "prompt_id": prompt_id
        }
        
    except Exception as e:
        return {"error": f"Execution failed: {str(e)}"}

# Запуск обработчика RunPod
runpod.serverless.start({"handler": handler})
