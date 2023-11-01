"""Backend test abstraction."""
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

COURSE_RUN_TEST_RESPONSE = {
    "next": "http://testserver/eox-nelp/api/v1/course_runs/?page=2",
    "previous": None,
    "count": 2,
    "num_pages": 2,
    "current_page": 1,
    "start": 0,
    "results": [
        {
            "schedule": {
                "start": "2033-02-02T00:00:00Z",
                "end": None,
                "enrollment_start": "2023-01-30T00:00:00Z",
                "enrollment_end": None,
            },
            "pacing_type": "instructor_paced",
            "team": [{"user": "vader", "role": "instructor"}, {"user": "vader", "role": "staff"}],
            "id": "course-v1:edX+cd101+2023-t2",
            "title": "PROCEDURAL SEDATION AND ANALGESIA COURSE",
            "images": {
                "card_image": "http://testserver/asset-v1:edX+cd101+2023-t2+type@asset+block@images_course_image.jpg",
            },
        },
        {
            "schedule": {
                "start": "2022-10-19T00:00:00Z",
                "end": "2022-10-31T00:00:00Z",
                "enrollment_start": "2022-10-01T00:00:00Z",
                "enrollment_end": "2022-10-17T00:00:00Z",
            },
            "pacing_type": "instructor_paced",
            "team": [{"user": "vader", "role": "instructor"}, {"user": "vader", "role": "staff"}],
            "id": "course-v1:edX+completion+2023",
            "title": "Course test h",
            "images": {
                "card_image": "http://testserver/asset-v1:edX+completion+2023+type@asset+block@logo-edunext-07.png",
            },
        },
    ],
}


def get_course_runs_view():
    """Return test class.
    Returns:
        TestCourseRunViewSet class.
    """
    return TestCourseRunsViewSet


class TestCourseRunsViewSet(GenericViewSet):
    """Test version of CourseRunViewSet."""

    def list(self, request, *args, **kwargs):  # pylint: disable=unused-argument
        return Response(COURSE_RUN_TEST_RESPONSE)

    def create(self, request, *args, **kwargs):  # pylint: disable=unused-argument
        return Response(request.data, status=status.HTTP_201_CREATED)
