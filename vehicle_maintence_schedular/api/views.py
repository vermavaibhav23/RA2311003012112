import requests
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .logger import Log

ACCESS_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJNYXBDbGFpbXMiOnsiYXVkIjoiaHR0cDovLzIwLjI0NC41Ni4xNDQvZXZhbHVhdGlvbi1zZXJ2aWNlIiwiZW1haWwiOiJ2djQ4MzRAc3JtaXN0LmVkdS5pbiIsImV4cCI6MTc3NzcwMTkyNywiaWF0IjoxNzc3NzAxMDI3LCJpc3MiOiJBZmZvcmQgTWVkaWNhbCBUZWNobm9sb2dpZXMgUHJpdmF0ZSBMaW1pdGVkIiwianRpIjoiZTcyZTYxMTgtZTA3Zi00N2FmLWIyNjYtNDI1YTFiYTliOWI2IiwibG9jYWxlIjoiZW4tSU4iLCJuYW1lIjoidmFpYmhhdiB2ZXJtYSIsInN1YiI6Ijg4MmYyYzhiLWZiNDAtNDQ1YS1hMjcwLTY1MzM0MDFlYTI2MiJ9LCJlbWFpbCI6InZ2NDgzNEBzcm1pc3QuZWR1LmluIiwibmFtZSI6InZhaWJoYXYgdmVybWEiLCJyb2xsTm8iOiJyYTIzMTEwMDMwMTIxMTIiLCJhY2Nlc3NDb2RlIjoiUWticHhIIiwiY2xpZW50SUQiOiI4ODJmMmM4Yi1mYjQwLTQ0NWEtYTI3MC02NTMzNDAxZWEyNjIiLCJjbGllbnRTZWNyZXQiOiJ1eE1lQndmQ1NKQ2dFZ1JWIn0._9313w_w04dzwN0EDqNdqecxzHkxHGmqwAmmfYFrJuQ"
BASE_URL = "http://20.207.122.201/evaluation-service"

def auth_headers():
    return {"Authorization": f"Bearer {ACCESS_TOKEN}"}

def fetch_depots():
    Log("backend", "info", "service", "Fetching depots from evaluation service")
    resp = requests.get(f"{BASE_URL}/depots", headers=auth_headers(), timeout=10)
    resp.raise_for_status()
    depots = resp.json()["depots"]
    Log("backend", "info", "service", f"Received {len(depots)} depots from API")
    return depots

def fetch_vehicles():
    Log("backend", "info", "service", "Fetching vehicles from evaluation service")
    resp = requests.get(f"{BASE_URL}/vehicles", headers=auth_headers(), timeout=10)
    resp.raise_for_status()
    vehicles = resp.json()["vehicles"]
    Log("backend", "info", "service", f"Received {len(vehicles)} vehicle tasks from API")
    return vehicles

def knapsack(capacity, vehicles):
    n = len(vehicles)
    dp = [[0] * (capacity + 1) for _ in range(n + 1)]

    for i in range(1, n + 1):
        d = vehicles[i - 1]['Duration']
        imp = vehicles[i - 1]['Impact']
        for w in range(capacity + 1):
            dp[i][w] = dp[i - 1][w]
            if d <= w:
                dp[i][w] = max(dp[i][w], dp[i - 1][w - d] + imp)

    selected = []
    w = capacity
    for i in range(n, 0, -1):
        if dp[i][w] != dp[i - 1][w]:
            selected.append(vehicles[i - 1])
            w -= vehicles[i - 1]['Duration']

    return dp[n][capacity], selected

@require_http_methods(["GET"])
def schedule_all(request):
    Log("backend", "info", "handler", "GET /api/schedule - computing schedule for all depots")

    try:
        depots = fetch_depots()
        vehicles = fetch_vehicles()
    except Exception as e:
        Log("backend", "error", "handler", f"Failed to fetch data from evaluation service: {str(e)}")
        return JsonResponse({"error": "Could not fetch depot/vehicle data"}, status=500)

    result = []
    for depot in depots:
        depot_id = depot['ID']
        capacity = depot['MechanicHours']

        Log("backend", "debug", "service", f"Running knapsack for depot {depot_id} with {capacity} mechanic-hours")
        max_impact, selected = knapsack(capacity, vehicles)
        hours_used = sum(t['Duration'] for t in selected)

        Log("backend", "info", "service", f"Depot {depot_id}: {len(selected)} tasks selected, impact={max_impact}, hours used={hours_used}/{capacity}")

        result.append({
            "depot_id": depot_id,
            "mechanic_hours_available": capacity,
            "hours_used": hours_used,
            "total_impact": max_impact,
            "tasks_count": len(selected),
            "tasks": [
                {"task_id": t['TaskID'], "duration": t['Duration'], "impact": t['Impact']}
                for t in selected
            ]
        })

    Log("backend", "info", "handler", f"Schedule computed successfully for {len(result)} depots")
    return JsonResponse({"schedule": result})

@require_http_methods(["GET"])
def schedule_depot(request, depot_id):
    Log("backend", "info", "handler", f"GET /api/schedule/{depot_id} - computing schedule for single depot")

    try:
        depots = fetch_depots()
        vehicles = fetch_vehicles()
    except Exception as e:
        Log("backend", "error", "handler", f"Failed to fetch data for depot {depot_id}: {str(e)}")
        return JsonResponse({"error": "Could not fetch depot/vehicle data"}, status=500)

    depot = next((d for d in depots if d['ID'] == depot_id), None)
    if not depot:
        Log("backend", "warn", "handler", f"Depot {depot_id} not found in depot list")
        return JsonResponse({"error": f"Depot {depot_id} not found"}, status=404)

    capacity = depot['MechanicHours']
    Log("backend", "debug", "service", f"Running knapsack for depot {depot_id}, capacity={capacity}h")

    max_impact, selected = knapsack(capacity, vehicles)
    hours_used = sum(t['Duration'] for t in selected)

    Log("backend", "info", "service", f"Depot {depot_id} result: impact={max_impact}, hours={hours_used}/{capacity}, tasks={len(selected)}")

    return JsonResponse({
        "depot_id": depot_id,
        "mechanic_hours_available": capacity,
        "hours_used": hours_used,
        "total_impact": max_impact,
        "tasks_count": len(selected),
        "tasks": [
            {"task_id": t['TaskID'], "duration": t['Duration'], "impact": t['Impact']}
            for t in selected
        ]
    })
