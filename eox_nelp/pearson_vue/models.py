"""
Database models for Pearson VUE service.

This module defines models for storing data related to the Pearson VUE service.

Classes:
    PearsonRTENEvent: A model representing an event for the Pearson VUE RTEN service.

Constants:
    EVENT_TYPE_CHOICES: A list of tuples representing the possible choices
        for an event type. Each choice represents a different type of event.
"""
from django.db import models

from eox_nelp.pearson_vue.constants import (
    CANCEL_APPOINTMENT,
    MODIFY_APPOINTMENT,
    MODIFY_RESULT_STATUS,
    PLACE_HOLD,
    RELEASE_HOLD,
    RESULT_NOTIFICATION,
    REVOKE_RESULT,
    UNREVOKE_RESULT,
)

EVENT_TYPE_CHOICES = [
    (RESULT_NOTIFICATION, "Result Notification"),
    (PLACE_HOLD, "Place Hold"),
    (RELEASE_HOLD, "Release Hold"),
    (MODIFY_RESULT_STATUS, "Modify Result Status"),
    (REVOKE_RESULT, "Revoke Result"),
    (UNREVOKE_RESULT, "Unrevoke Result"),
    (MODIFY_APPOINTMENT, "Modify Appointment"),
    (CANCEL_APPOINTMENT, "Cancel Appointment"),
]


class PearsonRTENEvent(models.Model):
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
