"""This file contains all the test for the course_experience views.py file.
Classes:
    LikeDislikeUnitExperienceTestCase: Test LikeDislikeUnitExperienceView.
"""
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from eox_nelp.course_experience.models import LikeDislikeCourse, LikeDislikeUnit, ReportCourse, ReportUnit
from eox_nelp.edxapp_wrapper.course_overviews import CourseOverview

from .mixins_helpers import BASE_COURSE_ID, BASE_ITEM_ID, CourseExperienceTestMixin, UnitExperienceTestMixin


class LikeDislikeUnitExperienceTestCase(UnitExperienceTestMixin, APITestCase):
    """ Test LikeDislikeUnitExperience view """

    reverse_viewname_list = "course-experience-api:v1:like-units-list"
    reverse_viewname_detail = "course-experience-api:v1:like-units-detail"
    object_key = "item_id"
    patch_data = {"status": True}
    post_data = {
        "item_id": "block-v1:edX+cd1011+2020t1+type@vertical+block@new_item2",
        "status": False,
        "course_id": {
            "type": "CourseOverview",
            "id": f"{BASE_COURSE_ID}",
        }
    }

    def setUp(self):
        """
        Set variables and objects that depends in other class vars.
        Using self(LikeDislikeUnitExperienceTestCase).
        """
        super().setUp()
        self.my_unit_like, _ = LikeDislikeUnit.objects.get_or_create(  # pylint: disable=no-member
            item_id=BASE_ITEM_ID,
            course_id=self.my_course,
            author_id=self.user.id,
            status=False,
        )
        self.base_data = {
            "data": {
                "type": "LikeDislikeUnit",
                "id": f"{self.my_unit_like.id}",
                "attributes": {
                    "username": f"{self.user.username}",
                    "status": self.my_unit_like.status,
                    "item_id": f"{self.my_unit_like.item_id}",
                },
                "relationships": {
                    "author": {
                        "data": {
                            "type": "User",
                            "id": f"{self.user.id}",
                        }
                    },
                    "course_id": {
                        "data": {
                            "type": "CourseOverview",
                            "id": f"{self.my_course.id}",
                        }
                    }
                }
            }
        }
        self.object_url_kwarg = {self.object_key: BASE_ITEM_ID}


class ReportUnitExperienceTestCase(UnitExperienceTestMixin, APITestCase):
    """ Test ReportUnitExperience view """

    reverse_viewname_list = "course-experience-api:v1:report-units-list"
    reverse_viewname_detail = "course-experience-api:v1:report-units-detail"
    object_key = "item_id"
    patch_data = {"reason": "HA"}
    post_data = {
        "item_id": "block-v1:edX+cd1011+2020t1+type@vertical+block@new_item",
        "reason": "OO",
        "course_id": {
            "type": "CourseOverview",
            "id": f"{BASE_COURSE_ID}"
        }
    }

    def setUp(self):
        """
        Set variables and objects that depends in other class vars.
        Using self(ReportUnitExperienceTestCase).
        """
        super().setUp()
        self.my_unit_report, _ = ReportUnit.objects.get_or_create(  # pylint: disable=no-member
            item_id=BASE_ITEM_ID,
            course_id=self.my_course,
            author_id=self.user.id,
            reason="Sexual content",
        )
        self.base_data = {
            "data": {
                "type": "ReportUnit",
                "id": f"{self.my_unit_report.id}",
                "attributes": {
                    "username": f"{self.user.username}",
                    "reason": f"{self.my_unit_report.reason}",
                    "item_id": f"{self.my_unit_report.item_id}",
                },
                "relationships": {
                    "author": {
                        "data": {
                            "type": "User",
                            "id": f"{self.user.id}",
                        }
                    },
                    "course_id": {
                        "data": {
                            "type": "CourseOverview",
                            "id": f"{self.my_course.id}",
                        }
                    }
                }
            }
        }
        self.object_url_kwarg = {self.object_key: BASE_ITEM_ID}

    def test_post_wrong_reason(self):
        """
        Test a  post request sending a not valid choice reason.
        Expected behavior:
            - Return expected content not valid choice.
            - Status code 404.
        """
        data = self.base_data
        url_endpoint = reverse(self.reverse_viewname_list)
        data["item_id"] = "block-v1:edX+cd1011+2020t1+type@vertical+block@new_item_reason"
        data["reason"] = "not valid choice reason"

        response = self.client.post(url_endpoint, data, format="json", contentType="application/json")

        self.assertContains(response, "is not a valid choice.", status_code=status.HTTP_400_BAD_REQUEST)


class LikeDislikeCourseExperienceTestCase(CourseExperienceTestMixin, APITestCase):
    """ Test LikeDislikeCourseExperience view """

    reverse_viewname_list = "course-experience-api:v1:like-courses-list"
    reverse_viewname_detail = "course-experience-api:v1:like-courses-detail"
    object_key = "course_id"
    change_field = "status"
    new_object_id = "course-v1:edX+cd101+2023-new_course"
    patch_data = {"status": True}
    post_data = {
        "course_id": {
            "type": "CourseOverview",
            "id": f"{new_object_id}"
        },
        "status": True
    }

    def setUp(self):
        """
        Set variables and objects that depends in other class vars.
        Using self(LikeDislikeCourseExperienceTestCase).
        """
        super().setUp()
        self.my_course_like, _ = LikeDislikeCourse.objects.get_or_create(  # pylint: disable=no-member
            course_id=self.my_course,
            author_id=self.user.id,
            status=False,
        )
        self.object_url_kwarg = {self.object_key: BASE_COURSE_ID}
        # add another course due the post doesnt work without existent courseoverview
        self.my_new_course, _ = CourseOverview.objects.get_or_create(id=self.new_object_id)
        self.base_data = {
            "data": {
                "type": "LikeDislikeCourse",
                "id": f"{self.my_course_like.id}",
                "attributes": {
                    "username": f"{self.user.username}",
                    "status": self.my_course_like.status,
                },
                "relationships": {
                    "author": {
                        "data": {
                            "type": "User",
                            "id": f"{self.user.id}",
                        }
                    },
                    "course_id": {
                        "data": {
                            "type": "CourseOverview",
                            "id": f"{self.my_course.id}",
                        }
                    }
                }
            }
        }


class ReportCourseExperienceTestCase(CourseExperienceTestMixin, APITestCase):
    """ Test ReportCourseExperience view """
    reverse_viewname_list = "course-experience-api:v1:report-courses-list"
    reverse_viewname_detail = "course-experience-api:v1:report-courses-detail"
    object_key = "course_id"
    change_field = "reason"
    new_object_id = "course-v1:edX+cd101+2023-new_course"
    patch_data = {"reason": "HA"}
    post_data = {
        "course_id": {
            "type": "CourseOverview",
            "id": f"{new_object_id}",
        },
        "reason": "GV",
    }

    def setUp(self):
        """
        Set variables and objects that depends in other class vars.
        Using self(ReportCourseExperienceTestCase).
        """
        super().setUp()
        self.my_course_report, _ = ReportCourse.objects.get_or_create(  # pylint: disable=no-member
            course_id=self.my_course,
            author_id=self.user.id,
            reason="Sexual content",
        )
        self.object_url_kwarg = {self.object_key: BASE_COURSE_ID}
        self.my_new_course, _ = CourseOverview.objects.get_or_create(id=self.new_object_id)
        self.base_data = {
            "data": {
                "type": "ReportCourse",
                "id": f"{self.my_course_report.id}",
                "attributes": {
                    "username": f"{self.user.username}",
                    "reason": f"{self.my_course_report.reason}"
                },
                "relationships": {
                    "author": {
                        "data": {
                            "type": "User",
                            "id": f"{self.user.id}"
                        }
                    },
                    "course_id": {
                        "data": {
                            "type": "CourseOverview",
                            "id": f"{self.my_course.id}"
                        }
                    }
                }
            }
        }
