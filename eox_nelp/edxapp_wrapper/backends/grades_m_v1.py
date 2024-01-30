"""Backend for lms grades djangoapp.
This file contains all the necessary grades dependencies from
https://github.com/eduNEXT/edunext-platform/tree/ednx-release/mango.master/lms/djangoapps/grade
"""
from lms.djangoapps.grades.subsection_grade_factory import SubsectionGradeFactory  # pylint: disable=import-error


def get_subsection_grade_factory():
    """Allow to get the SubsectionGradeFactory class from
    https://github.com/eduNEXT/edunext-platform/blob/ednx-release/mango.master/lms/djangoapps/grades/subsection_grade_factory.py#L27
    Returns:
        SubsectionGradeFactory class.
    """
    return SubsectionGradeFactory
