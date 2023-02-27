"""Serializers used for the experience views."""
from rest_framework_json_api import serializers

from eox_nelp.course_experience.models import LikeDislikeCourse, LikeDislikeUnit, ReportCourse, ReportUnit


class ExperienceSerializer(serializers.ModelSerializer):
    """Class to configure serializer for Experiences.

    Ancestors:
        serializer (serializers.ModelSerializer): the model serializer from json api

    """
    username = serializers.CharField(
        source="author.username", required=False, allow_blank=True
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
