import runpod
import requests
import time
import base64
from urllib.parse import urlencode

COMFY_URL = "http://127.0.0.1:8188"

# сколько максимум ждать одну генерацию (сек)
MAX_WAIT_SEC = 300
POLL_INTERVAL = 1.0

def _comfy_post_prompt(workflow: dict) -> str:
    payload = {
        "prompt": workflow,
        "client_id": "runpod_serverless"
    }
    r = requests.post(f"{COMFY_URL}/prompt", json=payload, timeout=60)
    r.raise_for_status()
    data = r.json()
    prompt_id = data.get("prompt_id")
    if not prompt_id:
        raise RuntimeError(f"comfy returned no prompt_id: {data}")
    return prompt_id

def _comfy_get_history(prompt_id: str) -> dict:
    r = requests.get(f"{COMFY_URL}/history/{prompt_id}", timeout=60)
    r.raise_for_status()
    return r.json()

def _extract_images_from_history(history: dict, prompt_id: str) -> list[dict]:
    """
    Возвращает список объектов вида:
    {"filename": "...", "subfolder": "...", "type": "output"}
    """
    if prompt_id not in history:
        return []

    item = history[prompt_id]
    outputs = item.get("outputs", {})
    images = []

    for _node_id, node_out in outputs.items():
        for img in node_out.get("images", []) or []:
            # comfy обычно отдаёт filename/subfolder/type
            fn = img.get("filename")
            if not fn:
                continue
            images.append({
                "filename": fn,
                "subfolder": img.get("subfolder", ""),
                "type": img.get("type", "output"),
            })

    return images

def _download_comfy_image(meta: dict) -> bytes:
    # /view?filename=...&subfolder=...&type=...
    query = urlencode({
        "filename": meta["filename"],
        "subfolder": meta.get("subfolder", ""),
        "type": meta.get("type", "output")
    })
    url = f"{COMFY_URL}/view?{query}"
    r = requests.get(url, timeout=120)
    r.raise_for_status()
    return r.content

def handler(job):
    try:
        job_input = job.get("input") or {}
        workflow = job_input.get("workflow")

        if not isinstance(workflow, dict):
            return {
                "error": "missing_or_invalid_workflow",
                "message": "expected job.input.workflow to be an object (dict)"
            }

        # 1) отправляем граф в ComfyUI
        prompt_id = _comfy_post_prompt(workflow)

        # 2) ждём появления в history
        t0 = time.time()
        images_meta = []

        while time.time() - t0 < MAX_WAIT_SEC:
            history = _comfy_get_history(prompt_id)
            images_meta = _extract_images_from_history(history, prompt_id)
            # если outputs появились, но картинок ещё нет — подождём чуть
            if prompt_id in history and history[prompt_id].get("outputs") is not None and images_meta:
                break
            time.sleep(POLL_INTERVAL)

        if not images_meta:
            # попробуем вернуть полезную диагностику
            history = _comfy_get_history(prompt_id)
            item = history.get(prompt_id, {})
            return {
                "error": "no_images",
                "message": "workflow executed but produced no images (or timed out)",
                "prompt_id": prompt_id,
                "history_keys": list(item.keys())
            }

        # 3) скачиваем картинки и возвращаем base64
        out_images = []
        for meta in images_meta:
            img_bytes = _download_comfy_image(meta)
            out_images.append({
                "filename": meta["filename"],
                "mime": "image/png",
                "data_base64": base64.b64encode(img_bytes).decode("utf-8")
            })

        return {
            "status": "success",
            "prompt_id": prompt_id,
            "images": out_images
        }

    except requests.HTTPError as e:
        # покажем тело ответа, если есть
        try:
            body = e.response.text
        except Exception:
            body = None
        return {
            "error": "http_error",
            "message": str(e),
            "response_body": body
        }
    except Exception as e:
        return {"error": "exception", "message": str(e)}

runpod.serverless.start({"handler": handler})
