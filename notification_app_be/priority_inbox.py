import requests
import heapq
from datetime import datetime, timezone

ACCESS_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJNYXBDbGFpbXMiOnsiYXVkIjoiaHR0cDovLzIwLjI0NC41Ni4xNDQvZXZhbHVhdGlvbi1zZXJ2aWNlIiwiZW1haWwiOiJ2djQ4MzRAc3JtaXN0LmVkdS5pbiIsImV4cCI6MTc3NzcwNjMzNSwiaWF0IjoxNzc3NzA1NDM1LCJpc3MiOiJBZmZvcmQgTWVkaWNhbCBUZWNobm9sb2dpZXMgUHJpdmF0ZSBMaW1pdGVkIiwianRpIjoiNWNhY2VjYjQtYzBlMS00YjE2LWE1ZWUtODgzNTAzYjIyMzNjIiwibG9jYWxlIjoiZW4tSU4iLCJuYW1lIjoidmFpYmhhdiB2ZXJtYSIsInN1YiI6Ijg4MmYyYzhiLWZiNDAtNDQ1YS1hMjcwLTY1MzM0MDFlYTI2MiJ9LCJlbWFpbCI6InZ2NDgzNEBzcm1pc3QuZWR1LmluIiwibmFtZSI6InZhaWJoYXYgdmVybWEiLCJyb2xsTm8iOiJyYTIzMTEwMDMwMTIxMTIiLCJhY2Nlc3NDb2RlIjoiUWticHhIIiwiY2xpZW50SUQiOiI4ODJmMmM4Yi1mYjQwLTQ0NWEtYTI3MC02NTMzNDAxZWEyNjIiLCJjbGllbnRTZWNyZXQiOiJ1eE1lQndmQ1NKQ2dFZ1JWIn0.3xMNMXJhFotyQKs8tdWMYBCzDOQIOGPsrNCYMSatXLg"

WEIGHT = {
    "Placement": 3,
    "Result": 2,
    "Event": 1
}

def get_score(notification):
    weight = WEIGHT.get(notification["Type"], 1)
    created = datetime.strptime(notification["Timestamp"], "%Y-%m-%d %H:%M:%S")
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    seconds_old = (now - created).total_seconds()
    score = (weight * 86400) - seconds_old
    return score

def fetch_notifications():
    resp = requests.get(
        "http://20.207.122.201/evaluation-service/notifications",
        headers={"Authorization": f"Bearer {ACCESS_TOKEN}"},
        timeout=10
    )
    return resp.json()["notifications"]

def get_top_n(notifications, n=10):
    top = heapq.nlargest(n, notifications, key=get_score)
    return top

def add_new_notification(heap, new_notification, n=10):
    score = get_score(new_notification)
    heapq.heappush(heap, (score, new_notification))
    if len(heap) > n:
        heapq.heappop(heap)
    return heap

if __name__ == "__main__":
    notifications = fetch_notifications()
    top10 = get_top_n(notifications, n=10)

    print("Top 10 Priority Notifications\n")
    for i, n in enumerate(top10, 1):
        print(f"{i}. [{n['Type']}] {n['Message']}")
        print(f"   Timestamp: {n['Timestamp']}  |  Score: {round(get_score(n), 2)}")
        print()
