"""This file contains all the test for the pearson vue  utils.py file.
"""
from unittest.mock import MagicMock, patch

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings

from eox_nelp.pearson_vue_engine.models import PearsonEngine
from eox_nelp.pearson_vue_engine.utils import (
    generate_action_parameters,
    get_platform_data,
    get_user_data,
    update_user_engines,
)

User = get_user_model()


class TestUpdateUserEngineCustomForm(TestCase):
    """Class to test update_user_engines function"""
    # pylint: disable=no-member

    def test_creates_pearson_engine_if_none_exists(self):
        """Tests if a `PearsonEngine` instance is created if it doesn't exist.

        Expected Behavior:

        - If a `PearsonEngine` instance does not exist for the given user,
        a new instance should be created and associated with the user.
        """

        user = User.objects.create(username="not_exists_rti_user")

        update_user_engines(user, "cdd")

        self.assertIsInstance(user.pearsonengine, PearsonEngine)

    def test_increments_trigger_for_cdd(self):
        """Tests if the `increment_trigger` method is called and the trigger count is incremented.
        Expected Behavior:
        - The `cdd_triggers` attribute of the `PearsonEngine` instance should be incremented by 1.
        - Other colums would not be affected
        """
        initial_cdd_count = 12
        user = User.objects.create(username="incrementcdd")
        PearsonEngine.objects.create(user=user, cdd_triggers=initial_cdd_count)

        update_user_engines(user, "cdd")

        user.pearsonengine.refresh_from_db()
        self.assertEqual(user.pearsonengine.cdd_triggers, initial_cdd_count + 1)
        self.assertEqual(user.pearsonengine.ead_triggers, 0)
        self.assertEqual(user.pearsonengine.rti_triggers, 0)
        self.assertDictEqual(user.pearsonengine.courses, {})

    def test_increments_course_value_for_ead(self):
        """Tests if the `increment_course_value` method is called for "ead" actions
        and the course count is incremented.
        Expected Behavior:
        - The `rti_triggers` attribute of the `PearsonEngine` instance should be incremented by 1.
        - The course dict would be increment by one in the desired course.
        - Other colums would not be affected
        """
        initial_ead_count = 23
        course_id = "course-v1:test+awesome"
        initial_course_id_count = 99
        user = User.objects.create(username="incrementead")
        PearsonEngine.objects.create(
            user=user,
            ead_triggers=initial_ead_count,
            courses={
                course_id: initial_course_id_count
            }
        )

        update_user_engines(user, "ead", course_id)
        user.pearsonengine.refresh_from_db()

        self.assertEqual(user.pearsonengine.ead_triggers, initial_ead_count + 1)
        self.assertEqual(user.pearsonengine.cdd_triggers, 0)
        self.assertEqual(user.pearsonengine.rti_triggers, 0)
        self.assertEqual(user.pearsonengine.courses[course_id], initial_course_id_count + 1)

    def test_increments_course_value_for_rti(self):
        """Tests if the `increment_course_value` method is called for "rti" actions
        and the course count is incremented.
        Test not previous pearson engine one-one-relation instance but created.
        Expected Behavior:
        - The `rti_triggers` attribute of the `PearsonEngine` instance should be incremented by 1.
        - The course dict would be increment by one in the desired course.
        - Other colums would not be affected
        """
        user = User.objects.create(username="incrementrti")
        course_id = "course-v1:test+awesome"

        update_user_engines(user, "rti", course_id)

        user.pearsonengine.refresh_from_db()
        self.assertEqual(user.pearsonengine.rti_triggers, 1)
        self.assertEqual(user.pearsonengine.ead_triggers, 0)
        self.assertEqual(user.pearsonengine.cdd_triggers, 0)
        self.assertEqual(user.pearsonengine.courses[course_id], 1)

    def test_does_not_increment_course_value_for_other_actions(self):
        """Tests if the `increment_course_value` method is not called for other action names.
        Expected Behavior:

        - If the `action_name` is not "ead", "rti" or "cdd", raise ValueError.
        - The pearsonengine attributes should remain unchanged.
        """
        user = User.objects.create(
            username="otheactionincrement",
            pearsonengine=PearsonEngine.objects.create()
        )
        course_id = "course-v1:test+awesome"

        with self.assertRaises(ValueError):
            update_user_engines(user, "other_action", course_id)

        self.assertEqual(user.pearsonengine.cdd_triggers, 0)
        self.assertEqual(user.pearsonengine.ead_triggers, 0)
        self.assertEqual(user.pearsonengine.rti_triggers, 0)
        self.assertDictEqual(user.pearsonengine.courses, {})


class TestGetUserData(TestCase):
    """Test case for get_user_data."""

    def setUp(self):
        """
        Set up the test environment.
        """
        self.user = MagicMock(
            username="testuser",
            first_name="Test",
            last_name="User",
            email="test@example.com",
            profile=MagicMock(
                country=MagicMock(code="US"),
                name="Test User",
                city="Test City",
                phone_number="123-456-7890",
                mailing_address="123 Test St",
            ),
            extrainfo=MagicMock(
                arabic_name="اسم المستخدم",
                arabic_first_name="الاسم الاول",
                arabic_last_name="اسم العائلة",
                national_id="123456789",
            )
        )

    def test_get_user_data(self):
        """
        Test get_user_data function with all user data available, including national_id.

        Expected behavior:
            - The result is a dict with all user data.
        """
        expected_result = {
            "username": self.user.username,
            "full_name": self.user.profile.name,
            "first_name": self.user.first_name,
            "last_name": self.user.last_name,
            "email": self.user.email,
            "country": self.user.profile.country.code,
            "city": self.user.profile.city,
            "phone": self.user.profile.phone_number,
            "address": self.user.profile.mailing_address,
            "arabic_full_name": self.user.extrainfo.arabic_name,
            "arabic_first_name": self.user.extrainfo.arabic_first_name,
            "arabic_last_name": self.user.extrainfo.arabic_last_name,
            "national_id": self.user.extrainfo.national_id,
        }

        result = get_user_data(self.user)

        self.assertEqual(result, expected_result)


class TestGetPlatformData(TestCase):
    """Test case for get_platform_data."""

    @override_settings(PLATFORM_NAME="Test Platform", EDNX_TENANT_DOMAIN="test.example.com")
    def test_get_platform_data_with_tenant(self):
        """
        Test get_platform_data function with PLATFORM_NAME and EDNX_TENANT_DOMAIN defined.

        Expected behavior:
            - The result is a dict with platform name and tenant domain.
        """
        expected_result = {
            "name": settings.PLATFORM_NAME,
            "tenant": settings.EDNX_TENANT_DOMAIN,
        }

        result = get_platform_data()

        self.assertEqual(result, expected_result)

    @override_settings(PLATFORM_NAME="Test Platform")
    def test_get_platform_data_without_tenant(self):
        """
        Test get_platform_data function with only PLATFORM_NAME defined.

        Expected behavior:
            - The result is a dict with platform name and tenant is None.
        """
        expected_result = {
            "name": settings.PLATFORM_NAME,
            "tenant": None,
        }

        result = get_platform_data()

        self.assertEqual(result, expected_result)


class TestGenerateActionParameters(TestCase):
    """Test case for generate_action_parameters."""

    def setUp(self):
        """
        Set up the test environment.
        """
        self.mock_get_user_data = self.patch("eox_nelp.pearson_vue_engine.utils.get_user_data")
        self.mock_get_platform_data = self.patch("eox_nelp.pearson_vue_engine.utils.get_platform_data")

        self.mock_get_user_data.return_value = {"user_data": "mock"}
        self.mock_get_platform_data.return_value = {"platform_data": "mock"}

    def patch(self, target, **kwargs):
        """Patch a target and return the mock"""
        patcher = patch(target, **kwargs)
        mock = patcher.start()
        self.addCleanup(patcher.stop)
        return mock

    def test_generate_action_parameters(self):
        """
        Test generate_action_parameters function with exam_id.

        Expected behavior:
            - The result is a dict with user_data, platform_data, and exam_data.
            - get_user_data, get_platform_data, and get_exam_data are called once.
            - get_exam_data is called with exam_id.
        """
        user = MagicMock()
        exam_id = "exam123"

        result = generate_action_parameters(user, exam_id)

        self.assertEqual(result, {
            "user_data": {"user_data": "mock"},
            "platform_data": {"platform_data": "mock"},
            "exam_data": {"external_key": exam_id},
        })
        self.mock_get_user_data.assert_called_once_with(user)
        self.mock_get_platform_data.assert_called_once()
