import uuid
from django.db import models

class Notification(models.Model):
    TYPE_CHOICES = [
        ('placement', 'Placement'),
        ('event', 'Event'),
        ('result', 'Result'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def to_dict(self):
        return {
            "id": str(self.id),
            "type": self.type,
            "title": self.title,
            "message": self.message,
            "is_read": self.is_read,
            "created_at": self.created_at.isoformat(),
        }
