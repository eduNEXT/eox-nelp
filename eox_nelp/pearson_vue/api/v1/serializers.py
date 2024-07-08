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

    content = serializers.JSONField()

    class Meta:
        """Meta class"""
        model = PearsonRTENEvent
        fields = ["event_type", "content", "candidate", "created_at"]
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
