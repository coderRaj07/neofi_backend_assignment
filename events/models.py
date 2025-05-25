import uuid
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Event(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    location = models.CharField(max_length=255, blank=True, null=True)
    is_recurring = models.BooleanField(default=False)
    recurrence_pattern = models.JSONField(blank=True, null=True)  # e.g., {"frequency": "weekly", "interval": 1}
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_events')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def has_role(self, user, role):
        return self.permissions.filter(user=user, role__iexact=role).exists()

class EventVersion(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='versions')
    version_number = models.PositiveIntegerField()
    title = models.CharField(max_length=255)
    description = models.TextField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    location = models.CharField(max_length=255, blank=True, null=True)
    modified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['event', 'version_number'], name='unique_event_version'),]
        ordering = ['-version_number']
    
class EventPermission(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ROLE_CHOICES = (
        ('owner', 'Owner'),
        ('editor', 'Editor'),
        ('viewer', 'Viewer'),
    )
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='permissions')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)

    class Meta:
        # unique_together = ('event', 'user')  # used constraints adapting modern approach
        constraints = [models.UniqueConstraint(fields=['event', 'user'], name='unique_event_user'),]
