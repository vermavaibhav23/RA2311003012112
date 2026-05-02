import requests

ACCESS_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJNYXBDbGFpbXMiOnsiYXVkIjoiaHR0cDovLzIwLjI0NC41Ni4xNDQvZXZhbHVhdGlvbi1zZXJ2aWNlIiwiZW1haWwiOiJ2djQ4MzRAc3JtaXN0LmVkdS5pbiIsImV4cCI6MTc3NzcwMTkyNywiaWF0IjoxNzc3NzAxMDI3LCJpc3MiOiJBZmZvcmQgTWVkaWNhbCBUZWNobm9sb2dpZXMgUHJpdmF0ZSBMaW1pdGVkIiwianRpIjoiZTcyZTYxMTgtZTA3Zi00N2FmLWIyNjYtNDI1YTFiYTliOWI2IiwibG9jYWxlIjoiZW4tSU4iLCJuYW1lIjoidmFpYmhhdiB2ZXJtYSIsInN1YiI6Ijg4MmYyYzhiLWZiNDAtNDQ1YS1hMjcwLTY1MzM0MDFlYTI2MiJ9LCJlbWFpbCI6InZ2NDgzNEBzcm1pc3QuZWR1LmluIiwibmFtZSI6InZhaWJoYXYgdmVybWEiLCJyb2xsTm8iOiJyYTIzMTEwMDMwMTIxMTIiLCJhY2Nlc3NDb2RlIjoiUWticHhIIiwiY2xpZW50SUQiOiI4ODJmMmM4Yi1mYjQwLTQ0NWEtYTI3MC02NTMzNDAxZWEyNjIiLCJjbGllbnRTZWNyZXQiOiJ1eE1lQndmQ1NKQ2dFZ1JWIn0._9313w_w04dzwN0EDqNdqecxzHkxHGmqwAmmfYFrJuQ"

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
