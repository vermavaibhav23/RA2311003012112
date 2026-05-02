import requests

ACCESS_TOKEN = "paste_your_token_here"

def Log(stack, level, pkg, message):
    try:
        requests.post(
            "http://20.207.122.201/evaluation-service/logs",
            json={"stack": stack, "level": level, "package": pkg, "message": message},
            headers={"Authorization": f"Bearer {ACCESS_TOKEN}"},
            timeout=5
        )
    except Exception:
        pass
