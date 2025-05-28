"""
Test file for eox_core serializers.
"""
from custom_reg_form.models import ExtraInfo
from django.contrib.auth import get_user_model
from django.test import TestCase

from eox_nelp.eox_core.api.v1.serializers import NelpUserReadOnlySerializer

User = get_user_model()


class NelpUserReadOnlySerializerTestCase(TestCase):
    """Test case for NelpUserReadOnlySerializer."""

    def setUp(self):
        """Set up test case."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass'
        )

        # Create ExtraInfo instance
        self.extra_info = ExtraInfo.objects.create(  # pylint: disable=no-member
            user=self.user,
            national_id='1234567890',
            arabic_name='اسم عربي',
            arabic_first_name='الاسم الأول',
            arabic_last_name='اسم العائلة'
        )

    def test_to_representation(self):
        """Test serializer's to_representation method.

        Expected behavior:
            - Returns serialized data with extrainfo
            - Extrainfo contains all expected fields
        """
        serializer = NelpUserReadOnlySerializer(self.user)

        data = serializer.data

        self.assertIn('extrainfo', data)
        self.assertEqual(data['extrainfo']['national_id'], '1234567890')
        self.assertEqual(data['extrainfo']['arabic_name'], 'اسم عربي')
        self.assertEqual(data['extrainfo']['arabic_first_name'], 'الاسم الأول')
        self.assertEqual(data['extrainfo']['arabic_last_name'], 'اسم العائلة')
