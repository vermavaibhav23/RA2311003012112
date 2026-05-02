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

---

# Stage 2

## Database Choice

I am using **SQLite** for this system.

SQLite is a file-based database that comes built into Python and Django — no installation or configuration needed. For a campus notification platform with a few thousand students, it handles the load perfectly fine. The data structure is simple and fixed, so a lightweight SQL database is the right choice. There is no need for a separate database server, which keeps the setup simple.

---

## DB Schema

```sql
CREATE TABLE notifications (
    id TEXT PRIMARY KEY,
    type TEXT NOT NULL CHECK (type IN ('placement', 'event', 'result')),
    title TEXT NOT NULL,
    message TEXT NOT NULL,
    is_read INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
```

Indexes to add:

```sql
CREATE INDEX idx_notifications_type ON notifications(type);
CREATE INDEX idx_notifications_is_read ON notifications(is_read);
CREATE INDEX idx_notifications_created_at ON notifications(created_at DESC);
```

---

## Problems as Data Volume Grows

**1. Slow queries**
As the table grows to millions of rows, queries like `SELECT * FROM notifications` or `WHERE is_read = FALSE` will become slow because the database has to scan the entire table.

**2. Unread notifications piling up**
If students ignore notifications, the `is_read = FALSE` rows keep growing. Any query filtering on `is_read` slows down.

**3. Storage bloat**
Old notifications from months or years ago take up space and slow down every query even though nobody reads them.

**How to solve these:**

- Add indexes (already shown above) so the DB doesn't do full table scans
- Add pagination to every list endpoint so we never fetch all rows at once
- Archive or delete notifications older than 90 days with a scheduled job

---

## SQL Queries for Each API

**GET /api/notifications — fetch all**
```sql
SELECT * FROM notifications
ORDER BY created_at DESC;
```

**GET /api/notifications?type=placement — filter by type**
```sql
SELECT * FROM notifications
WHERE type = 'placement'
ORDER BY created_at DESC;
```

**GET /api/notifications/\<id\> — fetch one**
```sql
SELECT * FROM notifications
WHERE id = 'a1b2c3d4-e5f6-7890-abcd-ef1234567890';
```

**POST /api/notifications/create — insert new**
```sql
INSERT INTO notifications (id, type, title, message)
VALUES ('a1b2c3d4-e5f6-7890-abcd-ef1234567890', 'placement', 'Google Drive on Campus', 'Google visiting on 10th May.');
```

**PATCH /api/notifications/\<id\>/read — mark one as read**
```sql
UPDATE notifications
SET is_read = TRUE
WHERE id = 'a1b2c3d4-e5f6-7890-abcd-ef1234567890';
```

**PATCH /api/notifications/read-all — mark all as read**
```sql
UPDATE notifications
SET is_read = TRUE
WHERE is_read = FALSE;
```

**DELETE /api/notifications/\<id\>/delete — delete one**
```sql
DELETE FROM notifications
WHERE id = 'a1b2c3d4-e5f6-7890-abcd-ef1234567890';
```

**GET /api/notifications/unread-count — count unread**
```sql
SELECT COUNT(*) FROM notifications
WHERE is_read = FALSE;
```
