"""Test backend for eox-coreusers module."""
from django.contrib.auth.models import User
from django.db import models
from eox_core.edxapp_wrapper.backends.users_q_v1_test import *
from rest_framework import serializers

from eox_nelp.edxapp_wrapper.test_backends import create_test_model


def get_user_signup_source():
    """Return test model.

    Returns:
        UserSignupSource dummy model.
    """
    user_signup_source_fields = {
        "user": models.ForeignKey(User, db_index=True, on_delete=models.CASCADE),
        "site": models.CharField(max_length=255, db_index=True),
    }

    return create_test_model(
        "UserSignupSource", "eox_nelp", __package__, user_signup_source_fields,
    )



class NelpEdxappUserReadOnlySerializer(serializers.Serializer):
    """Mock serializer for NelpEdxappUserReadOnlySerializer."""
    username = serializers.CharField()
    email = serializers.EmailField()
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


    def to_representation(self, user):
        """Mock to_representation method."""
        return {
            'username': user.username,
            'email': user.email,
        }


def get_user_read_only_serializer():
    """Return test model.

    Returns:
        UserSignupSource dummy model.
    """
    return NelpEdxappUserReadOnlySerializer
