import requests


OLLAMA_URL = "http://localhost:11434/api/chat"
OLLAMA_TAGS_URL = "http://localhost:11434/api/tags"
OLLAMA_TIMEOUT_SECONDS = 420
DEFAULT_MODEL = "qwen2.5:0.5b"


def query_ollama(model: str, system: str, user_msg: str) -> str:
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": user_msg},
    ]
    payload = {
        "model": model,
        "messages": messages,
        "stream": False,
        "options": {
            "temperature": 0.2,
            "num_ctx": 4096,
            "num_predict": 900,
        },
        "keep_alive": "10m",
    }
    try:
        resp = requests.post(OLLAMA_URL, json=payload, timeout=OLLAMA_TIMEOUT_SECONDS)
        resp.raise_for_status()
        return resp.json()["message"]["content"]
    except requests.exceptions.ConnectionError:
        return (
            "**Ollama nicht erreichbar.**\n\n"
            "Bitte starten Sie Ollama und laden Sie ein lokales Modell."
        )
    except requests.exceptions.ReadTimeout:
        return (
            "**Fehler: Lokales KI-Modell hat zu lange gebraucht.**\n\n"
            "Bitte versuchen Sie es erneut mit kürzeren Notizen, dem Modell `qwen2.5:0.5b`, "
            "oder starten Sie Ollama neu. Die Anfrage wurde nicht an externe Dienste gesendet."
        )
    except requests.exceptions.HTTPError as e:
        detail = ""
        if e.response is not None:
            try:
                detail = e.response.json().get("error", "")
            except Exception:
                detail = e.response.text
        return f"**Fehler:** {e}\n\n{detail}".strip()
    except Exception as e:
        return f"**Fehler:** {e}"


def get_ollama_models() -> list[str]:
    try:
        resp = requests.get(OLLAMA_TAGS_URL, timeout=5)
        models = [m["name"] for m in resp.json().get("models", [])]
        preferred = ["qwen2.5:0.5b", "llama3.2:1b", "phi3:mini", "llama3:latest"]
        models.sort(key=lambda name: preferred.index(name) if name in preferred else len(preferred))
        return models if models else ["qwen2.5:0.5b", "llama3", "mistral"]
    except Exception:
        return ["qwen2.5:0.5b", "llama3", "mistral"]
