"""This file contains mixins to use for experience views test cases.
Mixins:
    - ExperienceTestMixin.
    - UnitExperienceTestMixin
    - CourseExperienceTestMixin
"""
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from eox_nelp.course_experience.api.v1.views import INVALID_KEY_ERROR
from eox_nelp.edxapp_wrapper.course_overviews import CourseOverview

User = get_user_model()

RESPONSE_CONTENT_TYPES = ["application/vnd.api+json", "application/json"]
BASE_ITEM_ID = "block-v1:edX+cd1011+2020t1+type@vertical+block@base_item"
BASE_COURSE_ID = "course-v1:edX+cd101+2023-t2"


class ExperienceTestMixin:
    """
    A mixin class with base experience setup configuration for testing.
    """
    def setUp(self):  # pylint: disable=invalid-name
        """
        Set base variables and objects across experience test cases.
        """
        self.client = APIClient()
        self.user, _ = User.objects.get_or_create(username="vader")
        self.my_course, _ = CourseOverview.objects.get_or_create(id=BASE_COURSE_ID)
        self.client.force_authenticate(self.user)

    def test_get_object_list_by_user(self):
        """ Test a  get  request to the list endpoint for the desired view.
        Expected behavior:
            - Return expected content type.
            - Status code 200.
            - Return a json list  with at least one object.
        """
        url_endpoint = reverse(self.reverse_viewname_list)

        response = self.client.get(url_endpoint)

        self.assertIn(response.headers["Content-Type"], RESPONSE_CONTENT_TYPES)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.json()['data'])
        for element in response.json()['data']:
            self.assertEqual(element["attributes"]["username"], self.user.username)
            self.assertEqual(element["relationships"]["author"]["data"]["id"], str(self.user.id))

    def test_not_authenticated_user(self):
        """
        Test disallow by credentials the  get  request to the list endpoint
         for the desired view.
        Expected behavior:
            - Return expected content.
            - Status code 401.
        """
        self.client.force_authenticate(user=None)
        url_endpoint = reverse(self.reverse_viewname_list)

        response = self.client.get(url_endpoint)

        self.assertContains(
            response, "Authentication credentials were not provided",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )

    def test_patch_object_json(self):
        """
        Test a  patch  request to the detail endpoint for the desired view
        using form data (type xhr in browser).
        Expected behavior:
            - Return expected content type.
            - Status code 200.
            - Check the response is equal to the expected patched.
        """
        url_endpoint = reverse(self.reverse_viewname_detail, kwargs=self.object_url_kwarg)
        expected_data = self.base_data.copy()
        expected_data["data"]["attributes"].update(self.patch_data)

        response = self.client.patch(url_endpoint, self.patch_data, format="json")

        self.assertIn(response.headers["Content-Type"], RESPONSE_CONTENT_TYPES)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), expected_data)

    def test_patch_object_form_data(self):
        """
        Test a  patch  request to the detail endpoint for the desired view
        using form data (type document in browser).
        Expected behavior:
            - Return expected content type.
            - Status code 200.
            - Check the response is equal to the expected patched.
        """
        url_endpoint = reverse(self.reverse_viewname_detail, kwargs=self.object_url_kwarg)
        expected_data = self.base_data.copy()
        expected_data["data"]["attributes"].update(self.patch_data)

        response = self.client.patch(url_endpoint, self.patch_data, format="multipart")

        self.assertIn(response.headers["Content-Type"], RESPONSE_CONTENT_TYPES)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), expected_data)

    def test_block_url_object_regex(self):
        """
        Test block a request to the detail endpoint for the desired view
        if the object_id passed Using the  url doesnt match url regex.
        Expected behavior:
            - Return expected content type.
            - Status code 404.
        """
        raw_url_endpoint = f"{reverse(self.reverse_viewname_list)}wrong-regex"

        response = self.client.get(raw_url_endpoint)

        self.assertIn(response.headers["Content-Type"], ["text/html"])
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class UnitExperienceTestMixin(ExperienceTestMixin):
    """
    A mixin class with test to use  for testing UnitExperience Views.
    """
    def test_get_specific_item_id(self):
        """
        Test a  get  request to the detail endpoint for the desired view.
        Expected behavior:
            - Return expected content type.
            - Status code 200.
            - Match the response of item_id is eqal to the expected.
        """
        url_endpoint = reverse(self.reverse_viewname_detail, kwargs=self.object_url_kwarg)

        response = self.client.get(url_endpoint)

        self.assertIn(response.headers["Content-Type"], RESPONSE_CONTENT_TYPES)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), self.base_data)

    def test_get_wrong_item_id(self):
        """
        Test a  get  request to the detail endpoint for units views.
        Expected behavior:
            - Return expected content type.
            - Status code 404.
        """
        url_endpoint = reverse(self.reverse_viewname_detail, kwargs={self.object_key: "block-v1:wrong_shape"})

        response = self.client.get(url_endpoint)

        self.assertIn(response.headers["Content-Type"], RESPONSE_CONTENT_TYPES)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_not_found_item_id(self):
        """
        Test a  get  request with good shape but the item doesnt exist.
        Using the  detail endpoint for units views.
        Expected behavior:
            - Return expected content type.
            - Status code 404.
            - Return expected msg of Not found  in content.
        """
        url_endpoint = reverse(
            self.reverse_viewname_detail,
            kwargs={
                self.object_key: "block-v1:edX+cd1011+2020t1+type@vertical+block@not_exist"
            },
        )

        response = self.client.get(url_endpoint)

        self.assertIn(response.headers["Content-Type"], RESPONSE_CONTENT_TYPES)
        self.assertContains(response, "Not found.", status_code=status.HTTP_404_NOT_FOUND)

    def test_post_item_id(self):
        """
        Test a  post  request to the list endpoint for the desired view.
        Expected behavior:
            - Return expected content type.
            - Status code 201.
            - Check the response object item_id has the expected attributes field.
            - Check the response object item_id has the expected relationships field.
        """
        url_endpoint = reverse(self.reverse_viewname_list)
        expected_data = self.base_data.copy()
        expected_data["data"]["attributes"].update(
            {key: value for key, value in self.post_data.items() if key != "course_id"}
        )

        response = self.client.post(url_endpoint, self.post_data, format="json", contentType="application/json")

        self.assertIn(response.headers["Content-Type"], RESPONSE_CONTENT_TYPES)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json()["data"]["attributes"], expected_data["data"]["attributes"])
        self.assertEqual(response.json()["data"]["relationships"], expected_data["data"]["relationships"])

    def test_post_wrong_course_id_object(self):
        """
        Test a  post  request with wrong course_id  object.
        Using the  detail endpoint for units views.
        Expected behavior:
            - Return expected content type.
            - Return expected msg of Incorrect type for course_id object in content.
            - Status code 400.
        """
        url_endpoint = reverse(self.reverse_viewname_list)
        wrong_data = self.post_data.copy()
        wrong_data["course_id"] = "wrong-course"

        response = self.client.post(url_endpoint, wrong_data, format="json", contentType="application/json")

        self.assertIn(response.headers["Content-Type"], RESPONSE_CONTENT_TYPES)
        self.assertContains(
            response,
            "Incorrect type. Expected resource identifier object, received str.",
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    def test_post_wrong_course_id(self):
        """
        Test a  post  request with wrong course_id string  but good shape object,
        Using the  detail endpoint for units views.
        Expected behavior:
            - Return expected content type.
            - Return expected msg of wrong shape of  `INVALID_KEY_ERROR`.
            - Status code 400.
        """
        url_endpoint = reverse(self.reverse_viewname_list)
        wrong_data = self.post_data.copy()
        wrong_data["course_id"]["id"] = "wrong-course-id"

        response = self.client.post(url_endpoint, wrong_data, format="json", contentType="application/json")

        self.assertIn(response.headers["Content-Type"], RESPONSE_CONTENT_TYPES)
        self.assertEqual(response.data, INVALID_KEY_ERROR)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_not_found_course_id(self):
        """
        Test a  post  request with good course_id string, good shape object,
        but courseoverview not exist.
        Using the  detail endpoint for units views.
        Expected behavior:
            - Return expected content type.
            - Return expected msg of oject does not exist in content.
            - Status code 400.
        """
        url_endpoint = reverse(self.reverse_viewname_list)
        url_endpoint = reverse(self.reverse_viewname_list)
        wrong_data = self.post_data.copy()
        wrong_data["course_id"]["id"] = "course-v1:edX+cd101+2023-noexist"

        response = self.client.post(url_endpoint, wrong_data, format="json", contentType="application/json")

        self.assertIn(response.headers["Content-Type"], RESPONSE_CONTENT_TYPES)
        self.assertContains(response, "object does not exist.", status_code=status.HTTP_400_BAD_REQUEST)

    def test_patch_wrong_course_id(self):
        """
        Test a  patch  request with wrong course_id string, good shape object.
        Using the  detail endpoint for units views.
        Expected behavior:
            - Return expected content type.
            - Return expected INVALID_KEY_ERROR.
            - Status code 400.
        """
        url_endpoint = reverse(self.reverse_viewname_detail, kwargs=self.object_url_kwarg)
        wrong_patch_data = self.patch_data.copy()
        wrong_patch_data["course_id"] = {
            "type": "CourseOverview",
            "id": "wrong-course-id",
        }

        response = self.client.patch(url_endpoint, wrong_patch_data, format="json", contentType="application/json")

        self.assertIn(response.headers["Content-Type"], RESPONSE_CONTENT_TYPES)
        self.assertEqual(response.data, INVALID_KEY_ERROR)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class CourseExperienceTestMixin(ExperienceTestMixin):
    """
    A mixin class with test to use  for testing CourseExperience Views.
    """
    def test_get_specific_course_id(self):
        """
        Test a  get  request to the detail endpoint for the desired view.
        Expected behavior:
            - Return expected content type.
            - Status code 200.
            - Match the response object_key with the object_id passed Using the  url.
        """
        url_endpoint = reverse(self.reverse_viewname_detail, kwargs=self.object_url_kwarg)

        response = self.client.get(url_endpoint)
        self.assertIn(response.headers["Content-Type"], RESPONSE_CONTENT_TYPES)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), self.base_data)

    def test_get_wrong_course_id(self):
        """
        Test a  get  request to the detail endpoint for courses views.
        Expected behavior:
            - Return expected content type.
            - Status code 400.
            - Return expected msg of wrong course_key in content.
        """
        url_endpoint = reverse(self.reverse_viewname_detail, kwargs={self.object_key: "course-v1:wrong_shape"})

        response = self.client.get(url_endpoint)

        self.assertIn(response.headers["Content-Type"], RESPONSE_CONTENT_TYPES)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_not_found_course_id(self):
        """
        Test a  get  request to the detail endpoint for courses views.
        Expected behavior:
            - Return expected content type.
            - Status code 404.
            - Return expected msg of not found in content.
        """
        url_endpoint = reverse(
            self.reverse_viewname_detail,
            kwargs={self.object_key: "course-v1:edX+cd101+2023-not_exist"},
        )

        response = self.client.get(url_endpoint)

        self.assertIn(response.headers["Content-Type"], RESPONSE_CONTENT_TYPES)
        self.assertContains(response, "Not found.", status_code=status.HTTP_404_NOT_FOUND)

    def test_post_course_id(self):
        """
        Test a  post  request to the list endpoint for the desired view.
        Expected behavior:
            - Return expected content type.
            - Status code 201.
            - Check the response object of course_id has the expected attributes field.
            - Check the response object of course_id has the expected relationships field.
        """
        url_endpoint = reverse(self.reverse_viewname_list)
        expected_data = self.base_data.copy()
        expected_data["data"]["attributes"].update(
            {key: value for key, value in self.post_data.items() if key != "course_id"}
        )
        expected_data["data"]["relationships"]["course_id"]["data"]["id"] = self.post_data["course_id"]["id"]

        response = self.client.post(url_endpoint, self.post_data, format="json", contentType="application/json")

        self.assertIn(response.headers["Content-Type"], RESPONSE_CONTENT_TYPES)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json()["data"]["attributes"], expected_data["data"]["attributes"])
        self.assertEqual(response.json()["data"]["relationships"], expected_data["data"]["relationships"])

    def test_post_not_found_course_id(self):
        """
        Test a  post  request to the detail endpoint for courses views.
        Expected behavior:
            - Return expected content type.
            - Status code 400.
            - Return expected msg of object associated doesnt exist in content.
        """
        url_endpoint = reverse(self.reverse_viewname_list)
        data = self.post_data
        data["course_id"] = {
            "type": "CourseOverview",
            "id": "course-v1:edX+cd101+2023-not_exist"
        }

        response = self.client.post(url_endpoint, data, format="json", contentType="application/json")

        self.assertIn(response.headers["Content-Type"], RESPONSE_CONTENT_TYPES)
        self.assertContains(response, "object does not exist.", status_code=status.HTTP_400_BAD_REQUEST)
