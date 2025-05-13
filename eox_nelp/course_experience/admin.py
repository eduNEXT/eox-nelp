"""Course experience admin file.

Contains the admin models for user course experiences.

classes:
    LikeDislikeUnitAdmin: Admin class for LikeDislikeUnit model.
    LikeDislikeCourseAdmin: Admin class for LikeDislikeCourse model.
    ReportCourseAdmin: Admin class for ReportCourse model.
    ReportUnitAdmin: Admin class for ReportUnit model.
"""
from typing import Type

from django.contrib import admin
from django.contrib.auth import get_user_model

from eox_nelp.course_experience.models import (
    FeedbackCourse,
    FeedbackUnit,
    LikeDislikeCourse,
    LikeDislikeUnit,
    ReportCourse,
    ReportUnit,
)

User = get_user_model()


class BaseAdmin(admin.ModelAdmin):
    """Base class that allow to extract username from author field.

    methods:
        get_author_username: Returns username from User instance.
    """
    raw_id_fields = ["author", "course_id"]

    @admin.display(ordering="author__username", description="Author")
    def get_author_username(self, obj: Type[User]) -> str:
        """Return username from User instance"""
        return obj.author.username


class LikeDislikeUnitAdmin(BaseAdmin):
    """Admin class for LikeDislikeUnit.

    attributes:
        list_display: Fields to be shown in admin interface.
    """
    list_display = ("get_author_username", "status", "item_id", "course_id")


class LikeDislikeCourseAdmin(BaseAdmin):
    """Admin class for LikeDislikeCourse.

    attributes:
        list_display: Fields to be shown in admin interface.
    """
    list_display = ("get_author_username", "status", "course_id")


class ReportUnitAdmin(BaseAdmin):
    """Admin class for ReportUnit.

    attributes:
        list_display: Fields to be shown in admin interface.
    """
    list_display = ("get_author_username", "reason", "item_id", "course_id")


class ReportCourseAdmin(BaseAdmin):
    """Admin class for ReportCourse.

    attributes:
        list_display: Fields to be shown in admin interface.
    """
    list_display = ("get_author_username", "reason", "course_id")


class FeedbackUnitAdmin(BaseAdmin):
    """Admin class for FeedbackUnit.

    attributes:
        list_display: Fields to be shown in admin interface.
    """
    list_display = (
        "get_author_username",
        "item_id",
        "course_id",
        "rating_content",
        "feedback",
        "public",
    )


class FeedbackCourseAdmin(BaseAdmin):
    """Admin class for FeedbackCourse.

    attributes:
        list_display: Fields to be shown in admin interface.
    """
    list_display = (
        "get_author_username",
        "course_id",
        "rating_content",
        "feedback",
        "public",
        "rating_instructors",
        "recommended",
    )
    search_fields = ("course_id__id", "author__username", "feedback")
    list_filter = ("public", "rating_content", "rating_instructors")


admin.site.register(LikeDislikeUnit, LikeDislikeUnitAdmin)
admin.site.register(LikeDislikeCourse, LikeDislikeCourseAdmin)
admin.site.register(ReportUnit, ReportUnitAdmin)
admin.site.register(ReportCourse, ReportCourseAdmin)
admin.site.register(FeedbackUnit, FeedbackUnitAdmin)
admin.site.register(FeedbackCourse, FeedbackCourseAdmin)
