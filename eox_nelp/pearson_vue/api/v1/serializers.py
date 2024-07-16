"""
Serializers for Pearson VUE Models

This module contains serializers for models related to Pearson VUE.

Classes:
    PearsonRTENSerializer: A serializer for the PearsonRTENEvent that handles the
        'event_type', 'content', and 'created_at' fields.
"""
from rest_framework import serializers

from eox_nelp.pearson_vue.models import PearsonRTENEvent


class PearsonRTENSerializer(serializers.ModelSerializer):
    """
    Serializer for the PearsonRTENEvent.

    This serializer handles the 'event_type', 'content', and 'created_at' fields.
    The 'content' field is treated as a JSONField, allowing for flexible storage of
    structured data. The 'event_type' and 'created_at' fields are read-only.

    Methods:
        to_internal_value: Custom method to convert incoming data to internal value
            representation. This ensures that all incoming data is stored in the 'content'
            field as JSON.

    Attributes:
        content (serializers.JSONField): A field to handle JSON content.
    """
    course = serializers.SerializerMethodField()
    content = serializers.JSONField()

    class Meta:
        """Meta class"""
        model = PearsonRTENEvent
        fields = ["event_type", "content", "candidate", "course", "created_at"]
        read_only_fields = ["event_type", "created_at"]

    def to_internal_value(self, data):
        """
        Convert incoming data to internal value representation.

        Args:
            data (dict): The incoming data to be serialized.

        Returns:
            dict: A dictionary containing the serialized data.
        """
        return {"content": data}

    def get_course(self, obj):
        """
        Retrieves the course associated with the given object as a string.

        This method checks if the `course` attribute of the provided object exists.
        If it does, it returns the string representation of the course.
        Otherwise, it returns `None`.

        Args:
            obj (object): The object containing the `course` attribute.

        Returns:
            str or None: The string representation of the course if it exists, otherwise `None`.
        """
        return str(obj.course) if obj.course else None

    def to_representation(self, instance):
        """
        Convert the object instance to its dictionary representation.

        This method overrides the default `to_representation` method to include
        the candidate's username in the serialized representation.

        Args:
            instance (object): The object instance being serialized.

        Returns:
            dict: A dictionary representation of the object instance, including
                  the candidate's username if a candidate is associated with the instance.
                  If no candidate is associated, the value will be None.
        """
        representation = super().to_representation(instance)
        representation["candidate"] = instance.candidate.username if instance.candidate else None

        return representation
