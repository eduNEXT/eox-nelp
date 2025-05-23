"""Serializer to extend eox-core's NelpEdxappUser serializer."""
from django.forms.models import model_to_dict
from eox_core.edxapp_wrapper.users import get_user_read_only_serializer

NelpEdxappUserReadOnlySerializer = get_user_read_only_serializer()


class NelpUserReadOnlySerializer(NelpEdxappUserReadOnlySerializer):
    """
    Serializer to extend eox-core's NelpEdxappUser serializer.
    """
    def to_representation(self, user):
        """
        Overwrite to_native to handle custom logic since we are serializing three models as one here
        :param user: User object
        :return: Dict serialized account
        """
        data = super().to_representation(user)
        # Add custom data to the serialized output
        data["extrainfo"] = model_to_dict(user.extrainfo)

        return data
