"""
Database models for Pearson VUE service.

This module defines models for storing data related to the Pearson VUE service.

Classes:
    PearsonRTENModel: A model representing an event for the Pearson VUE RTEN service.

Constants:
    EVENT_TYPE_CHOICES: A list of tuples representing the possible choices
        for an event type. Each choice represents a different type of event.
"""
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
    """
    A model representing a Pearson VUE RTEN event.

    Attributes:
        content: The content of the event, stored as JSON.
        created_at: The timestamp of when the event was created.
        event_type: The type of the event, chosen from predefined choices.
    """
    content = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    event_type = models.CharField(max_length=20, choices=EVENT_TYPE_CHOICES)
