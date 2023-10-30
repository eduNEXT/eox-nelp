"""
CMS API v1 Views
"""
from eox_nelp.edxapp_wrapper.cms_api import CourseRunViewSet


class NelpCourseRunViewSet(CourseRunViewSet):
    """
    Nelp  version(flavour) of CourseRun Api View.
    To got it you could use the following path.
    {studio_url}/eox-nelp/api/v1/course_runs/
    """
