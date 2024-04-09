"""Test backend for eox-coreusers module."""
from django.contrib.auth.models import User
from django.db import models

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
