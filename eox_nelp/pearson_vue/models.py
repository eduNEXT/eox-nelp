from django.db import models

EVENT_TYPE_CHOICES = [
    ("resultNotification", "Result Notification"),
    ("placeHold", "Place Hold"),
    ("releaseHold", "Release Hold"),
    ("modifyResultStatus", "Modify Result Status"),
    ("revokeResult", "Revoke Result"),
    ("unrevokeResult", "Unrevoke Result"),
]


class PearsonRTENModel(models.Model):
    content = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    event_type = models.CharField(max_length=20, choices=EVENT_TYPE_CHOICES)
