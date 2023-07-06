"""Serializers used for the experience views."""
from django.contrib.auth import get_user_model
from rest_framework_json_api import serializers

from eox_nelp.course_experience.api.v1.relations import ExperienceResourceRelatedField
from eox_nelp.course_experience.models import (
    FeedbackCourse,
    LikeDislikeCourse,
    LikeDislikeUnit,
    ReportCourse,
    ReportUnit,
)
from eox_nelp.edxapp_wrapper.course_overviews import CourseOverview

User = get_user_model()


class ExperienceSerializer(serializers.ModelSerializer):
    """Class to configure serializer for Experiences.

    Ancestors:
        serializer (serializers.ModelSerializer): the model serializer from json api

    """
    username = serializers.CharField(
        source="author.username", required=False, allow_blank=True
    )
    course_id = ExperienceResourceRelatedField(
        queryset=CourseOverview.objects,
    )
    author = ExperienceResourceRelatedField(
        queryset=User.objects,
    )


class LikeDislikeUnitExperienceSerializer(ExperienceSerializer):
    """Class to configure serializer for LikeDislikeUnitExperience.

    Ancestors:
        UnitExperienceSerializer: the serializer for unit experiences.
    """
    class Meta:
        """Class to configure serializer with  model LikeDislikeUnit"""

        model = LikeDislikeUnit
        fields = "__all__"


class ReportUnitExperienceSerializer(ExperienceSerializer):
    """Class to configure serializer for ReportUnitExperience.

    Ancestors:
        UnitExperienceSerializer: the serializer for unit experiences.
    """
    class Meta:
        """Class to configure serializer with  model ReportUnit"""
        model = ReportUnit
        fields = "__all__"


class LikeDislikeCourseExperienceSerializer(ExperienceSerializer):
    """Class to configure serializer for LikeDislikeCourseExperience.

    Ancestors:
        UnitExperienceSerializer: the serializer for course experiences.
    """
    class Meta:
        """Class to configure serializer with  model LikeDislikeCourse"""
        model = LikeDislikeCourse
        fields = "__all__"


class ReportCourseExperienceSerializer(ExperienceSerializer):
    """Class to configure serializer for ReportCourseExperience.

    Ancestors:
        UnitExperienceSerializer: the serializer for unit experiences.
    """
    class Meta:
        """Class to configure serializer with  model ReportCourse"""
        model = ReportCourse
        fields = "__all__"


class FeedbackCourseExperienceSerializer(ExperienceSerializer):
    """Class to configure serializer for FeedbackCourseExperience.

    Ancestors:
        UnitExperienceSerializer: the serializer for unit experiences.
    """
    class Meta:
        """Class to configure serializer with  model ReportCourse"""
        model = FeedbackCourse
        fields = "__all__"
