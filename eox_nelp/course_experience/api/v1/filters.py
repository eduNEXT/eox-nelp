"""Filters used for the experience views."""

from django_filters.rest_framework import FilterSet

from eox_nelp.course_experience.models import FeedbackCourse


class FeedbackCourseFieldsFilter(FilterSet):
    """Filter class that configure the query params of a

    Args:
        FilterSet: Ancestor related filterset from rest framework.
    """
    class Meta:
        """Meta configuration for field for FeedbackCourse model. """
        model = FeedbackCourse
        fields = [
            "rating_content",
            "rating_instructors",
            "public",
            "recommended",
            "course_id__id",
            "author__username",
            "id",
        ]
