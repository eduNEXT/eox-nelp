"""This file contains all the test for the pearson vue  models.py file."""
from django.contrib.auth import get_user_model
from django.test import TestCase

from eox_nelp.pearson_vue.models import PearsonEngine

User = get_user_model()


class PearsonEngineTestCase(TestCase):
    """
    Test case for the PearsonEngine model.

    This test suite covers the functionality of the PearsonEngine model,
    including its methods for managing triggers and courses.

    Attributes:
        user (User): A test user for the PearsonEngine instances.
        engine (PearsonEngine): A PearsonEngine instance for testing.

    """
    # pylint: disable=no-member
    def setUp(self):
        """
        Set up the test environment before each test method.

        Creates a test user and a PearsonEngine instance associated with that user.
        """
        self.user, _ = User.objects.get_or_create(username='test-user', password='12345')
        self.engine, _ = PearsonEngine.objects.get_or_create(user=self.user)

    def test_trigger_operations(self):
        """
        Test trigger-related operations.

        Tests getting, setting, and incrementing triggers for different types.

        Expected behavior:
        - get_triggers should return the correct value for each trigger type.
        - set_triggers should update the trigger value correctly.
        - increment_trigger should increase the trigger value by the specified amount.
        - Invalid trigger types should raise ValueError.
        - Setting negative trigger values should raise ValueError.
        """
        # Test initial values
        self.assertEqual(self.engine.get_triggers('rti'), 0)
        self.assertEqual(self.engine.get_triggers('cdd'), 0)
        self.assertEqual(self.engine.get_triggers('ead'), 0)

        # Test setting triggers
        self.engine.set_triggers('rti', 5)
        self.assertEqual(self.engine.get_triggers('rti'), 5)

        # Test incrementing triggers
        self.engine.increment_trigger('cdd', 3)
        self.assertEqual(self.engine.get_triggers('cdd'), 3)

        # Test invalid trigger type
        with self.assertRaises(ValueError):
            self.engine.get_triggers('invalid')

        # Test setting negative value
        with self.assertRaises(ValueError):
            self.engine.set_triggers('ead', -1)

        # Test setting invalid value
        with self.assertRaises(ValueError):
            self.engine.set_triggers('invalid', 1)

    def test_course_operations(self):
        """
        Test course-related operations.

        Tests getting, setting, incrementing, and removing course values.

        Expected behavior:
        - get_courses should return the correct dictionary for each action type.
        - get_course_value should return the correct value for a specific course.
        - set_course_value should update the course value correctly.
        - increment_course_value should increase the course value by the specified amount.
        - remove_course should delete the course from the dictionary. ALso invalid type raise Valuerror.
        - Invalid action types should raise ValueError.
        - Setting negative course values should raise ValueError.
        """
        # Test setting and getting course values
        self.engine.set_course_value('course1', 10)
        self.engine.set_course_value('course33', 44)
        self.assertEqual(self.engine.get_course_value('course1'), 10)

        # Test incrementing course values
        self.engine.increment_course_value('course1', 5)
        self.assertEqual(self.engine.get_course_value('course1'), 15)

        # Test removing courses
        self.engine.remove_course('course1')
        self.engine.remove_course('course33')
        with self.assertRaises(ValueError):
            self.engine.remove_course('course1')

    def test_course_aggregation(self):
        """
        Test course aggregation methods.

        Tests getting course IDs and total course values.

        Expected behavior:
        - get_course_ids should return a list of all course IDs for a specific action.
        - get_total_course_value should return the sum of all course values for a specific action.
        """
        self.engine.set_course_value('course1', 10)
        self.engine.set_course_value('course2', 20)
        self.engine.set_course_value('course3', 30)

        self.assertEqual(set(self.engine.get_course_ids()), {'course1', 'course2', 'course3'})
        self.assertEqual(self.engine.get_total_course_value(), 60)

    def test_total_triggers_property(self):
        """
        Test the total_triggers property.

        Expected behavior:
        - total_triggers should return the sum of all trigger types.
        """
        self.engine.set_triggers('rti', 5)
        self.engine.set_triggers('cdd', 3)
        self.engine.set_triggers('ead', 2)
        self.assertEqual(self.engine.total_triggers, 10)

    def test_model_creation(self):
        """
        Test PearsonEngine model creation and default values.

        Expected behavior:
        - A new PearsonEngine instance should be created with default values.
        - The created_at and updated_at fields should be automatically set.
        """
        PearsonEngine.objects.all().delete()
        new_engine = PearsonEngine.objects.create(user=self.user)
        self.assertEqual(new_engine.rti_triggers, 0)
        self.assertEqual(new_engine.cdd_triggers, 0)
        self.assertEqual(new_engine.ead_triggers, 0)
        self.assertEqual(new_engine.courses, {})
        self.assertIsNotNone(new_engine.created_at)
        self.assertIsNotNone(new_engine.updated_at)

    def test_user_relationship(self):
        """
        Test the relationship between PearsonEngine and User models.

        Expected behavior:
        - Each PearsonEngine instance should be associated with a unique User.
        - Deleting a User should delete the associated PearsonEngine instance (CASCADE).
        """
        self.assertEqual(self.engine.user, self.user)
        User.objects.get(id=self.user.id).delete()
        with self.assertRaises(PearsonEngine.DoesNotExist):
            PearsonEngine.objects.get(id=self.engine.id)
