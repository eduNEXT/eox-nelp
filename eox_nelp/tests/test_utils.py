"""This file contains all the test for the utils.py file.

Classes:
    ExtractCourseIdFromStringTestCase: Tests cases for the extract_course_id_from_string method.
    GetCourseFromIdTestCase: Tests cases for the get_course_from_id method.
"""
from ddt import data, ddt
from django.test import TestCase
from mock import patch
from opaque_keys.edx.keys import CourseKey

from eox_nelp.utils import extract_course_id_from_string, get_course_from_id


@ddt
class ExtractCourseIdFromStringTestCase(TestCase):
    """Test class for the extract_course_id_from_string method."""

    @data(
        "this is a long string",
        "hjsdgafhawsdbfhsdyafgbhjsdbf1784561553415534",
        "this is a similar string course-v1:77777554a45sd4a2ad42s45d",
        "https://example.com/course/course-v1edx+CS105+2023-T3"
    )
    def test_course_id_not_found(self, value):
        """ Test that the method returns an empty string when any course_id is not found

        Expected behavior:
            - Returned value is an empty string
        """
        result = extract_course_id_from_string(value)

        self.assertEqual("", result)

    @data(
        ["course-v1:edx+PS874+2023-T3", "this is a course-v1:edx+PS874+2023-T3/) long string"],
        ["course-v1:edunext+CS105+2019-P3", "hjsdgafhawsdbfhgbhjsdbf1784561553415534course-v1:edunext+CS105+2019-P3"],
        ["course-v1:NELC+TR675+2022-K3", "this course-v1:NELC+TR675+2022-K3/ is a similar string course-v1:77775s45d"],
        ["course-v1:edx+CS105+2023-T3", "https://example.com/course/course-v1:edx+CS105+2023-T3"],
    )
    def test_course_id_found(self, value):
        """ Test that the method returns right course id.

        Expected behavior:
            - Returned value is the expected course id.
        """
        result = extract_course_id_from_string(value[1])

        self.assertEqual(value[0], result)

    def test_multiple_valid_ids(self):
        """ Test that the method returns the first value that matches the regular expression.

        Expected behavior:
            - Returned value is the expected course id.
        """
        string = (
            "/course-v1:edx+CS105+2023-T3/"
            "/course-v1:NELC+TR675+2022-K3/"
            "/course-v1:edx+PS874+2023-T3/"
            "/course-v1:edunext+CS105+2019-P3/"
        )

        result = extract_course_id_from_string(string)

        self.assertEqual("course-v1:edx+CS105+2023-T3", result)


class GetCourseFromIdTestCase(TestCase):
    """Test class for the get_course_from_id method."""

    @patch("eox_nelp.utils.get_course_overviews")
    def test_course_id_not_found(self, course_overviews_mock):
        """ Test that the method raises the right exception when there are no courses.

        Expected behavior:
            - Raises ValueError exception.
            - get_course_overviews method was called with the right parameter.
        """
        course_id = "course-v1:edx+CS105+2023-T3"
        course_overviews_mock.return_value = []

        self.assertRaises(ValueError, get_course_from_id, course_id)
        course_overviews_mock.assert_called_once_with([CourseKey.from_string(course_id)])

    @patch("eox_nelp.utils.get_course_overviews")
    def test_course_id_found(self, course_overviews_mock):
        """ Test that the method returns the expected value.

        Expected behavior:
            - Returned value is the expected course.
            - get_course_overviews method was called with the right parameter.
        """
        course_id = "course-v1:edx+CS105+2023-T3"
        expected_course = {"name": "test-course", "short_description": "This is a great course"}
        course_overviews_mock.return_value = [expected_course]

        course = get_course_from_id(course_id)

        self.assertEqual(expected_course, course)
        course_overviews_mock.assert_called_once_with([CourseKey.from_string(course_id)])
