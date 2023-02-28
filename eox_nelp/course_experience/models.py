"""
Course experience models. This contains all the model related with the course user experience.

Models:
    LikeDislikeUnit: Store user decision(like or dislike) for specific unit.
    LikeDislikeCourse: Store user decision(like or dislike) for a course.
    ReportUnit: Store report reason about a specific unit.
    ReportCourse: Store report reason for a course.
"""
from django.contrib.auth import get_user_model
from django.db import models
from opaque_keys.edx.django.models import UsageKeyField

from eox_nelp.edxapp_wrapper.course_overviews import CourseOverview

User = get_user_model()


class BaseLikeDislike(models.Model):
    """Base abstract model for like and dislike records.

    fields:
        author<Foreignkey>: Makes reference to the user record associated with the status.
        status<BooleanField>: True = Liked, False =d isliked and None = not-set
        course_id<Foreignkey>: Reference to a specific course.
    """
    author = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    status = models.BooleanField(null=True)
    course_id = models.ForeignKey(CourseOverview, null=True, on_delete=models.SET_NULL)

    class Meta:
        """Set model abstract"""
        abstract = True


class BaseReport(models.Model):
    """Base abstract model for reporting records.

    fields:
        author<Foreignkey>: Makes reference to the user record associated with the reason.
        reason<CharField>: Store report reason as a code, e.g SC => Sexual Content.
        course_id<Foreignkey>: Reference to a specific course.
    """
    REPORT_REASONS = [
        ("SC", "Sexual content"),
        ("GV", "Graphic violence"),
        ("HA", "Hateful or abusive content"),
        ("CI", "Copycat or impersonation"),
        ("OO", "Other objection"),
    ]

    author = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    reason = models.CharField(
        max_length=2,
        null=True,
        blank=True,
        choices=REPORT_REASONS,
        default=None
    )
    course_id = models.ForeignKey(CourseOverview, null=True, on_delete=models.SET_NULL)

    class Meta:
        """Set model abstract"""
        abstract = True


class LikeDislikeUnit(BaseLikeDislike):
    """Extends from BaseLikeDislike, this model will store an opinion about a specific unit.

    fields:
        item_id<UsageKeyField>: Unit identifier.
    """
    item_id = UsageKeyField(max_length=255)

    class Meta:
        """Set constrain for author an item id"""
        unique_together = [["author", "item_id"]]


class LikeDislikeCourse(BaseLikeDislike):
    """Extends from BaseLikeDislike, this model will store an opinion about a specific course
    and set constrains.
    """
    class Meta:
        """Set constrain for author an course id"""
        unique_together = [["author", "course_id"]]


class ReportUnit(BaseReport):
    """Extends from BaseReport, this model will store a report about a specific unit.

    fields:
        item_id<UsageKeyField>: Unit identifier.
    """
    item_id = UsageKeyField(max_length=255)

    class Meta:
        """Set constrain for author an item id"""
        unique_together = [["author", "item_id"]]


class ReportCourse(BaseReport):
    """Extends from BaseReport, this model will store a report about a specific course
    and set constrains.
    """
    class Meta:
        """Set constrain for author an course id"""
        unique_together = [["author", "course_id"]]
