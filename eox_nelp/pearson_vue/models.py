"""
Database models for Pearson VUE service.

This module defines models for storing data related to the Pearson VUE service.

Classes:
    PearsonRTENEvent: A model representing an event for the Pearson VUE RTEN service.
    PearsonEngine: A model representing the send to the PearsonEngine service per user.

Constants:
    EVENT_TYPE_CHOICES: A list of tuples representing the possible choices
        for an event type. Each choice represents a different type of event.
"""
from django.contrib.auth import get_user_model
from django.db import models

from eox_nelp.edxapp_wrapper.course_overviews import CourseOverview
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
User = get_user_model()


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
    candidate = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    course = models.ForeignKey(CourseOverview, null=True, on_delete=models.DO_NOTHING)


class PearsonEngine(models.Model):
    """
    This model contains data related to user and the integration with PearsonVue engine service.

    Attributes:
        user (User): OneToOne relationship with User model.
        rti_triggers (int): Number of RTI triggers.
        cdd_triggers (int): Number of CDD triggers.
        ead_triggers (int): Number of EAD triggers.
        courses (dict): JSON field storing EAD course data.
        created_at (datetime): Timestamp of model instance creation.
        updated_at (datetime): Timestamp of last model instance update.
    """

    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    rti_triggers = models.PositiveIntegerField(default=0)
    cdd_triggers = models.PositiveIntegerField(default=0)
    ead_triggers = models.PositiveIntegerField(default=0)
    courses = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_triggers(self, trigger_type):
        """
        Get the number of triggers for a specific type.

        Args:
            trigger_type (str): The type of trigger ('rti', 'cdd', or 'ead').

        Returns:
            int: The number of triggers for the specified type.

        Raises:
            ValueError: If an invalid trigger type is provided.
        """
        trigger_name = f"{trigger_type}_triggers"

        if not hasattr(self, trigger_name):
            raise ValueError(f"Invalid trigger name: {trigger_name}")

        return getattr(self, trigger_name, None)

    def set_triggers(self, trigger_type, value):
        """
        Set the number of triggers for a specific type.

        Args:
            trigger_type (str): The type of trigger ('rti', 'cdd', or 'ead').
            value (int): The new value for the trigger count.

        Raises:
            ValueError: If the value is not a non-negative integer or if an invalid trigger type is provided.
        """
        trigger_name = f"{trigger_type}_triggers"

        if not isinstance(value, int) or value < 0:
            raise ValueError("Trigger value must be a non-negative integer")

        if not hasattr(self, trigger_name):
            raise ValueError(f"Invalid trigger name: {trigger_name}")

        setattr(self, trigger_name, value)
        self.save()

    def increment_trigger(self, trigger_type, increment=1):
        """
        Increment the number of triggers for a specific type.

        Args:
            trigger_type (str): The type of trigger ('rti', 'cdd', or 'ead').
            increment (int, optional): The amount to increment. Defaults to 1.
        """
        current_value = self.get_triggers(trigger_type)
        self.set_triggers(trigger_type, current_value + increment)

    def get_courses(self):
        """
        Get the courses for a specific action type.

        Returns:
            dict: The courses for the specified action type.

        """
        return self.courses

    def get_course_value(self, course_id):
        """
        Get the value of a specific course.

        Args:
            course_id (str): The ID of the course.

        Returns:
            int: The value of the specified course, or 0 if not found.
        """
        courses = self.get_courses()
        return courses.get(course_id, 0)

    def set_course_value(self, course_id, value):
        """
        Set the value of a specific course.

        Args:
            course_id (str): The ID of the course.
            value (int or float): The new value for the course.

        Raises:
            ValueError: If the value is not a non-negative number.
        """
        if not isinstance(value, (int, float)) or value < 0:
            raise ValueError("Course value must be a non-negative number")
        courses = self.get_courses()
        courses[course_id] = value
        self.courses = courses
        self.save()

    def increment_course_value(self, course_id, increment=1):
        """
        Increment the value of a specific course.

        Args:
            course_id (str): The ID of the course.
            increment (int or float, optional): The amount to increment. Defaults to 1.
        """
        current_value = self.get_course_value(course_id)
        self.set_course_value(course_id, current_value + increment)

    def remove_course(self, course_id):
        """
        Remove a course from the specified action type.

        Args:
            course_id (str): The ID of the course to remove.

        Raises:
            ValueError: If the course is not found in the specified action type.
        """
        courses = self.get_courses()
        if course_id in courses:
            del courses[course_id]
            self.courses = courses
            self.save()
        else:
            raise ValueError(f"Course {course_id} not found in courses")

    def get_course_ids(self):
        """
        Get all course IDs for a specific action type.

        Returns:
            list: A list of all course IDs for the specified action type.
        """
        return list(self.get_courses().keys())

    def get_total_course_value(self):
        """
        Get the total value of all courses for a specific action type.

        Returns:
            float: The sum of all course values for the specified action type.
        """
        return sum(self.get_courses().values())

    @property
    def total_triggers(self):
        """
        Get the total number of triggers across all types.

        Returns:
            int: The sum of RTI, CDD, and EAD triggers.
        """
        return self.rti_triggers + self.cdd_triggers + self.ead_triggers
