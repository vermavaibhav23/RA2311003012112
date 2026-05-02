import json
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from .models import Notification
from .logger import Log


@csrf_exempt
@require_http_methods(["GET"])
def get_all_notifications(request):
    Log("backend", "info", "handler", "GET /api/notifications called")

    notification_type = request.GET.get("type", None)

    if notification_type:
        notifications = Notification.objects.filter(type=notification_type).order_by("-created_at")
        Log("backend", "debug", "service", f"Filtering notifications by type: {notification_type}")
    else:
        notifications = Notification.objects.all().order_by("-created_at")

    unread_count = Notification.objects.filter(is_read=False).count()

    Log("backend", "info", "service", f"Returning {notifications.count()} notifications, {unread_count} unread")

    return JsonResponse({
        "total": notifications.count(),
        "unread": unread_count,
        "notifications": [n.to_dict() for n in notifications]
    })


@csrf_exempt
@require_http_methods(["GET"])
def get_one_notification(request, notification_id):
    Log("backend", "info", "handler", f"GET /api/notifications/{notification_id} called")

    try:
        notification = Notification.objects.get(id=notification_id)
        Log("backend", "info", "service", f"Notification {notification_id} found and returned")
        return JsonResponse(notification.to_dict())
    except Notification.DoesNotExist:
        Log("backend", "warn", "handler", f"Notification {notification_id} not found")
        return JsonResponse({"error": "Notification not found"}, status=404)


@csrf_exempt
@require_http_methods(["POST"])
def create_notification(request):
    Log("backend", "info", "handler", "POST /api/notifications called")

    try:
        body = json.loads(request.body)
    except json.JSONDecodeError:
        Log("backend", "error", "handler", "Invalid JSON body in create notification request")
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    notification_type = body.get("type")
    title = body.get("title")
    message = body.get("message")

    if not notification_type or not title or not message:
        Log("backend", "warn", "handler", "Missing required fields: type, title, or message")
        return JsonResponse({"error": "type, title and message are required"}, status=400)

    if notification_type not in ["placement", "event", "result"]:
        Log("backend", "warn", "handler", f"Invalid notification type received: {notification_type}")
        return JsonResponse({"error": "type must be placement, event, or result"}, status=400)

    notification = Notification.objects.create(
        type=notification_type,
        title=title,
        message=message
    )

    Log("backend", "info", "service", f"New {notification_type} notification created with id {notification.id}")
    return JsonResponse(notification.to_dict(), status=201)


@csrf_exempt
@require_http_methods(["PATCH"])
def mark_one_read(request, notification_id):
    Log("backend", "info", "handler", f"PATCH /api/notifications/{notification_id}/read called")

    try:
        notification = Notification.objects.get(id=notification_id)
        notification.is_read = True
        notification.save()
        Log("backend", "info", "service", f"Notification {notification_id} marked as read")
        return JsonResponse({"message": "Notification marked as read", "id": str(notification.id)})
    except Notification.DoesNotExist:
        Log("backend", "warn", "handler", f"Notification {notification_id} not found for mark-read")
        return JsonResponse({"error": "Notification not found"}, status=404)


@csrf_exempt
@require_http_methods(["PATCH"])
def mark_all_read(request):
    Log("backend", "info", "handler", "PATCH /api/notifications/read-all called")

    count = Notification.objects.filter(is_read=False).count()
    Notification.objects.filter(is_read=False).update(is_read=True)

    Log("backend", "info", "service", f"Marked {count} notifications as read")
    return JsonResponse({"message": "All notifications marked as read"})


@csrf_exempt
@require_http_methods(["DELETE"])
def delete_notification(request, notification_id):
    Log("backend", "info", "handler", f"DELETE /api/notifications/{notification_id} called")

    try:
        notification = Notification.objects.get(id=notification_id)
        notification.delete()
        Log("backend", "info", "service", f"Notification {notification_id} deleted successfully")
        return JsonResponse({"message": "Notification deleted"})
    except Notification.DoesNotExist:
        Log("backend", "warn", "handler", f"Notification {notification_id} not found for deletion")
        return JsonResponse({"error": "Notification not found"}, status=404)


@csrf_exempt
@require_http_methods(["GET"])
def unread_count(request):
    Log("backend", "info", "handler", "GET /api/notifications/unread-count called")

    count = Notification.objects.filter(is_read=False).count()
    Log("backend", "debug", "service", f"Unread notification count: {count}")
    return JsonResponse({"unread_count": count})
