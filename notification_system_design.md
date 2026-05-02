# Stage 1

## Campus Notification Platform - REST API Design


## Headers

```
Authorization: Bearer <access_token>
Content-Type: application/json
```

---

## Notification Structure

```json
{
  "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "type": "placement",
  "title": "Google Drive on Campus",
  "message": "Google will be visiting campus on 10th May for placements.",
  "is_read": false,
  "created_at": "2026-05-02T10:30:00Z"
}
```

---

## Endpoints

### GET /api/notifications
Returns all notifications. Supports optional `?type=placement|event|result` filter.

Response:
```json
{
  "total": 3,
  "unread": 2,
  "notifications": [...]
}
```

---

### GET /api/notifications/\<id\>
Returns a single notification by ID.

Response 200:
```json
{
  "id": "...",
  "type": "event",
  "title": "Tech Fest",
  "message": "Annual tech fest on 15th May.",
  "is_read": false,
  "created_at": "2026-05-02T10:30:00Z"
}
```

Response 404:
```json
{ "error": "Notification not found" }
```

---

### POST /api/notifications/create
Creates a new notification.

Request:
```json
{
  "type": "result",
  "title": "Semester 6 Results Out",
  "message": "Check results on the student portal."
}
```

Response 201:
```json
{
  "id": "...",
  "type": "result",
  "title": "Semester 6 Results Out",
  "message": "Check results on the student portal.",
  "is_read": false,
  "created_at": "2026-05-02T11:00:00Z"
}
```

---

### PATCH /api/notifications/\<id\>/read
Marks a single notification as read.

Response:
```json
{ "message": "Notification marked as read", "id": "..." }
```

---

### PATCH /api/notifications/read-all
Marks all notifications as read.

Response:
```json
{ "message": "All notifications marked as read" }
```

---

### DELETE /api/notifications/\<id\>/delete
Deletes a notification.

Response:
```json
{ "message": "Notification deleted" }
```

---

### GET /api/notifications/unread-count
Returns count of unread notifications.

Response:
```json
{ "unread_count": 5 }
```

---

## Real-Time Notifications

Real-time delivery is handled using **WebSockets** via Django Channels.

When a student logs in, the frontend opens a WebSocket connection to:
```
ws://host/ws/notifications/
```

When a new notification is created, the server immediately pushes it to all connected clients:

```json
{
  "event": "new_notification",
  "data": {
    "id": "...",
    "type": "placement",
    "title": "Infosys On Campus",
    "message": "Infosys drive scheduled for 20th May.",
    "is_read": false,
    "created_at": "2026-05-02T12:00:00Z"
  }
}
```

Redis is used as the channel layer so messages are broadcast across all server instances.

---

## Error Format

All errors follow this structure:

```json
{ "error": "description" }
```

Status codes: `200`, `201`, `400`, `401`, `404`, `500`
