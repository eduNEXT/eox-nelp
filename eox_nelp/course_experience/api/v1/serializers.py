"""Serializers used for the experience views."""
from django.conf import settings
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
from eox_nelp.utils import map_instance_attributes_to_dict

User = get_user_model()
COURSE_OVERVIEW_EXTRA_FIELD_MAPPING = {"display_name": "display_name"}
USER_EXTRA_FIELD_MAPPING = {
    "first_name": "first_name",
    "last_name": "last_name",
    "profile_name": "profile__name",
    "username": "username",
}


def get_course_extra_attributes(value=None):
    """Function to retrieve CourseOverview extra fields

    Args:
        value (CourseOverview instance): CourseOverview that the relation analize. Defaults to None.

    Returns:
        dict: dict object too add course extra fields
    """
    course_overview_mapping = getattr(
        settings,
        "COURSE_EXPERIENCE_SETTINGS",
        {},
    ).get("COURSE_OVERVIEW_EXTRA_FIELD_MAPPING", COURSE_OVERVIEW_EXTRA_FIELD_MAPPING)

    return {"attributes": map_instance_attributes_to_dict(value, course_overview_mapping)}


def get_user_extra_attributes(value=None):
    """Function to retrieve User extra fields

    Args:
        value (Userinstance): User that the relation analize. Defaults to None.

    Returns:
        dict: dict object too add user extra fields
    """
    user_mapping = getattr(
        settings,
        "COURSE_EXPERIENCE_SETTINGS",
        {},
    ).get("USER_EXTRA_FIELD_MAPPING", USER_EXTRA_FIELD_MAPPING)

    return {"attributes": map_instance_attributes_to_dict(value, user_mapping)}


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
        get_extra_fields=get_course_extra_attributes,
    )
    author = ExperienceResourceRelatedField(
        queryset=User.objects,
        get_extra_fields=get_user_extra_attributes,
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
