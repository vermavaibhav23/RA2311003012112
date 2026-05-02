# Stage 1

## Notification System API Design

every request needs these headers

```
Authorization: Bearer <access_token>
Content-Type: application/json
```

a notification object looks like this

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

type can be placement, event or result

---

## API Endpoints

**GET /api/notifications**

get all notifications, can also filter by type using query param

```
GET /api/notifications
GET /api/notifications?type=placement
```

response:
```json
{
  "total": 3,
  "unread": 2,
  "notifications": [...]
}
```

---

**GET /api/notifications/\<id\>**

get one notification by its id

200 response:
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

if id doesnt exist:
```json
{ "error": "Notification not found" }
```

---

**POST /api/notifications/create**

create a new notification

request body:
```json
{
  "type": "result",
  "title": "Semester 6 Results Out",
  "message": "Check results on the student portal."
}
```

response (201):
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

**PATCH /api/notifications/\<id\>/read**

marks one notification as read

```json
{ "message": "Notification marked as read", "id": "..." }
```

---

**PATCH /api/notifications/read-all**

marks everything as read at once

```json
{ "message": "All notifications marked as read" }
```

---

**DELETE /api/notifications/\<id\>/delete**

delete a notification

```json
{ "message": "Notification deleted" }
```

---

**GET /api/notifications/unread-count**

just returns how many unread notifications there are

```json
{ "unread_count": 5 }
```

---

## Real Time Notifications

for real time i am using websockets so the frontend doesnt have to keep refreshing to check for new notifications.

when a student opens the app, it connects to:
```
ws://host/ws/notifications/
```

whenever a new notification is created on the backend, it gets pushed to the frontend immediately like this:

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

django channels handles the websocket part and redis is used so all server instances can share messages.

all errors come back as:
```json
{ "error": "what went wrong" }
```

---

# Stage 2

## Database

I used SQLite. its already built into python and django uses it by default so no extra setup is needed. since this is a campus platform and the data is simple (all notifications have the same fields every time), sqlite is more than enough for this.

## Schema

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

also added these indexes so queries don't get slow:

```sql
CREATE INDEX idx_notifications_type ON notifications(type);
CREATE INDEX idx_notifications_is_read ON notifications(is_read);
CREATE INDEX idx_notifications_created_at ON notifications(created_at DESC);
```

## Problems that can come up when data grows

first problem is that queries become slow. if there are lakhs of rows, doing SELECT * or filtering by is_read will take time because sqlite has to go through every row.

second is unread notifications keep piling up. students often dont read notifications so the table keeps growing with is_read = 0 rows and any count or filter query on that column gets slower.

third is old data just sitting there. notifications from 6 months ago are useless but still taking up space and slowing things down.

to fix these - indexes help a lot with the slow query problem. for the old data problem, a scheduled job that deletes notifications older than 90 days would work. and adding pagination so we never fetch all rows at once also helps.

## Queries

get all notifications
```sql
SELECT * FROM notifications
ORDER BY created_at DESC;
```

filter by type
```sql
SELECT * FROM notifications
WHERE type = 'placement'
ORDER BY created_at DESC;
```

get one by id
```sql
SELECT * FROM notifications
WHERE id = 'a1b2c3d4-e5f6-7890-abcd-ef1234567890';
```

insert new notification
```sql
INSERT INTO notifications (id, type, title, message)
VALUES ('a1b2c3d4-e5f6-7890-abcd-ef1234567890', 'placement', 'Google Drive on Campus', 'Google visiting on 10th May.');
```

mark one as read
```sql
UPDATE notifications
SET is_read = 1
WHERE id = 'a1b2c3d4-e5f6-7890-abcd-ef1234567890';
```

mark all as read
```sql
UPDATE notifications
SET is_read = 1
WHERE is_read = 0;
```

delete one
```sql
DELETE FROM notifications
WHERE id = 'a1b2c3d4-e5f6-7890-abcd-ef1234567890';
```

count unread
```sql
SELECT COUNT(*) FROM notifications
WHERE is_read = 0;
```

---

# Stage 3

the query in question:
```sql
SELECT * FROM notifications
WHERE studentID = 1042 AND isRead = false
ORDER BY createdAt DESC;
```

**is the query accurate?**

the query is logically doing the right thing - fetching unread notifications for a specific student sorted by newest first. but it will be very slow on a table with 5 million rows because there are no indexes on studentID or isRead so the database has to scan every single row to find matches.

**why is it slow?**

with 50,000 students and 5 million notifications, a full table scan on every request is expensive. every time a student opens the app this query runs and reads through millions of rows just to find a few hundred. no indexes means no shortcuts.

**what to change?**

add a composite index on studentID and isRead together since both are used in the WHERE clause:

```sql
CREATE INDEX idx_student_read ON notifications(studentID, isRead);
```

also adding createdAt to the index helps since we are sorting by it:

```sql
CREATE INDEX idx_student_read_date ON notifications(studentID, isRead, createdAt);
```

with this index the db goes directly to the rows for that student instead of scanning everything. cost goes from O(n) on 5 million rows to roughly O(log n) which is much faster.

**should we add indexes on every column?**

no, that is bad advice. indexes speed up reads but slow down writes. every INSERT or UPDATE has to update all the indexes too. if every column has an index, adding one notification becomes slow because the db has to update 6-7 indexes. also indexes take up extra storage. you should only index columns that are actually used in WHERE or ORDER BY.

**query to find students who got a placement notification in last 7 days**

```sql
SELECT DISTINCT studentID FROM notifications
WHERE notificationType = 'Placement'
AND createdAt >= NOW() - INTERVAL 7 DAY;
```

---

# Stage 4

the problem is that every time a student opens the app, a DB query runs. with 50,000 students doing this at the same time the database gets hit thousands of times per minute which is why it is getting overwhelmed.

**solution 1 - caching**

store the result of the notification query in cache (like Redis) for a short time, maybe 30-60 seconds. so instead of hitting the DB every time, most requests just read from cache.

tradeoff: a student might see slightly outdated notifications for up to 60 seconds. also you need to clear the cache when new notifications are added otherwise students wont see them immediately. adds some complexity to the code.

**solution 2 - pagination**

instead of fetching all notifications at once, fetch only 10 or 20 at a time. this reduces how much data the DB reads and returns each request.

tradeoff: frontend has to handle loading more notifications when the user scrolls down. but this is a very common pattern and worth doing regardless of other optimizations.

**solution 3 - only fetch unread count on load**

instead of fetching all notifications on every page load, just fetch the unread count. only fetch the full list when the student actually clicks on the notification bell. most students open the app without checking notifications so this avoids a lot of unnecessary queries.

tradeoff: slight delay when the student opens the notification panel since that triggers a query at that point. but this is better than hammering the DB on every single page load.

the best approach is combining all three - pagination + caching + lazy loading. caching alone can serve stale data, pagination alone still hits the DB, but together they reduce DB load significantly.

---

# Stage 5

**problems with the current implementation**

the main problem is everything is happening one by one inside a loop for 50,000 students. for each student it calls send_email, then saves to DB, then pushes to app. this means the whole thing runs synchronously and will take a very long time. the person who clicked "Notify All" is basically waiting for 50,000 emails to send before anything finishes.

also if send_email fails at student 200, the loop crashes or skips. the remaining 49,800 students get nothing. there is no retry logic and no way to know which students were missed.

**should DB save and email happen together?**

no they should not. email and in-app notification are two different things. if the email API is down, students should still get the in-app notification. tying them together means one failure breaks everything. they should be completely independent of each other.

**how to redesign this**

first save all notifications to DB in one bulk insert instead of 50,000 separate inserts. then push to app for all students. then put all the emails into a queue and process them separately in the background.

if an email fails it can be retried from the queue without affecting anything else.

```
function notify_all(student_ids, message):
    bulk_save_to_db(student_ids, message)
    push_to_app(student_ids, message)
    for student_id in student_ids:
        add_to_email_queue(student_id, message)

function process_email_queue():
    for each job in queue:
        success = send_email(job.student_id, job.message)
        if not success:
            retry(job)
```

**what to do about the 200 students whose email failed**

since emails go through a queue with retry logic, the failed ones will be retried automatically. we can also log which student_ids failed so if retries also fail, we know exactly who to resend to manually. the in-app notification already went through so at least they got notified inside the app.

---

# Stage 6

i fetch notifications from the API, filter only unread ones, then score each notification based on type and how recent it is. top 10 are picked using a heap.

**scoring formula**

placement gets weight 3, result gets 2, event gets 1. recency is calculated as seconds since the notification was created. the final score is:

```
score = (weight * 86400) - seconds_since_created
```

multiplying weight by 86400 (seconds in a day) means a placement notification has to be more than 1 day older than a result to lose priority to it. this keeps type as the main factor but recency still matters when types are equal or close.

**how top 10 is maintained as new notifications come in**

i use a min-heap of size 10. when a new notification arrives its score is calculated. if the score is higher than the lowest score already in the heap, it replaces it. this way we never have to re-sort the entire list, we just do one heap operation which is O(log 10) = basically constant time.
