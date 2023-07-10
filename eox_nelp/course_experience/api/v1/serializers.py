"""Serializers used for the experience views."""
from copy import copy

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
    return {
        "attributes": map_attributes_from_instance_to_dict(value, COURSE_OVERVIEW_EXTRA_FIELD_MAPPING)
    }


def get_user_extra_attributes(value=None):
    """Function to retrieve User extra fields

    Args:
        value (Userinstance): User that the relation analize. Defaults to None.

    Returns:
        dict: dict object too add user extra fields
    """
    return {
        "attributes": map_attributes_from_instance_to_dict(value, USER_EXTRA_FIELD_MAPPING)
    }


def map_attributes_from_instance_to_dict(instance, attributes_mapping):
    """Create a dictionary that represents some fields or attributes of a instance based on
    a attributes_mapping dictionary. This dict would have key, values which the key represent the
    attribute to look in the instance and the value the key name in the output dict.
    Based in the `attributes_mapping` you should use a dict with the following config:
    {
        "key_name": "field_name"
    }
    This would check in the instace instance.field_name and the value send it to output dict
    like {"key_name": instance.field_name}
    Also its is possible to check nested fields if you declarate the field of instance separated by `__`
    eg:
    {
        "key_name": "field_level1__field_level2"
    }
    This example would check in the instace like instance.field_level1.field_level2 and in the output
    dict like {"key_name": instance.field_level1.field_level2}
    Args:
        instance (instance class): Model or instance of class to retrieved fields.
        attributes_mapping (dict): Dictionary map that has the fields to search and the keys name to output,

    Returns:
        instance_dict: dict representing the instance
    """
    instance_dict = {}
    for extra_field, instance_field in attributes_mapping.items():
        extra_value = None
        instance_level = copy(instance)
        for instance_field in instance_field.split("__"):
            if hasattr(instance_level, instance_field):
                instance_level = getattr(instance_level, instance_field)
                extra_value = instance_level

        instance_dict[extra_field] = extra_value

    return instance_dict


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
