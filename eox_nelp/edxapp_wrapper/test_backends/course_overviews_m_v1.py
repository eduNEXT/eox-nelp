"""Test backend for course overviews module."""
from opaque_keys.edx.django.models import CourseKeyField

from eox_nelp.edxapp_wrapper.test_backends import create_test_model


def get_course_overview_model():
    """Return test model.
    Returns:
        CourseOverview dummy model.
    """
    course_overview_fields = {
        "id": CourseKeyField(db_index=True, primary_key=True, max_length=255),
        "__str__": lambda self: str(self.id),  # id is course_locator object
    }

    return create_test_model(
        "CourseOverview", "eox_nelp", __package__, course_overview_fields
    )
