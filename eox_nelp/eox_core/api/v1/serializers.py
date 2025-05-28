"""Serializer to extend eox-core's NelpEdxappUser serializer."""
from django.forms.models import model_to_dict
from eox_core.edxapp_wrapper.users import get_user_read_only_serializer

CoreEdxappUserReadOnlySerializer = get_user_read_only_serializer()


class NelpUserReadOnlySerializer(CoreEdxappUserReadOnlySerializer):
    """Serializer for extending eox-core's CoreEdxappUserReadOnly serializer.

    This serializer adds ExtraInfo fields to the base user serialization.

    Attributes:
        All attributes are inherited from CoreEdxappUserReadOnlySerializer.
    """

    def to_representation(self, user):
        """Convert User instance into a dict with ExtraInfo fields.

        Args:
            user: User model instance to be serialized.

        Returns:
            dict: Serialized user data including ExtraInfo fields if they exist,
                otherwise returns base user data with empty extrainfo dict.
        """
        data = super().to_representation(user)
        data["extrainfo"] = model_to_dict(user.extrainfo) if hasattr(user, 'extrainfo') and user.extrainfo else {}
        return data
