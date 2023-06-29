"""eox-nelp Metrics file.

functions:
    get_cached_courses: Return visible courses.
    get_course_metrics: Return the metric for the given course_key.
    get_learners_metric: Return number of learners, for the visible courses.
    get_instructors_metric: Return number of instructors, for the visible courses.
    get_courses_metrics: Return metrics for the visible courses.
"""
from django.conf import settings

from eox_nelp.edxapp_wrapper.branding import get_visible_courses
from eox_nelp.edxapp_wrapper.modulestore import modulestore
from eox_nelp.edxapp_wrapper.site_configuration import configuration_helpers
from eox_nelp.edxapp_wrapper.student import CourseAccessRole, CourseEnrollment
from eox_nelp.stats.decorators import cache_method


@cache_method
def get_cached_courses(tenant):  # pylint: disable=unused-argument
    """
    Returns the visible courses. This method is just a wrapper of get_visible_courses that
    allows to cache the result.

    Args:
        tenant<str>: String tenant identifier(site.domain)

    Return:
        list[<CourseOverview>]: List of CourseOverview records.
    """
    return get_visible_courses()


@cache_method
def get_course_metrics(course_key):
    """
    This allows to get the course stats metrics based on the course key.

    Args:
        course_key<opaque-key>: Course identifier.

    Return:
        <Dictionary>: Contains the course's metrics.
    """
    stats_settings = getattr(settings, "STATS_SETTINGS", {})
    course = modulestore().get_course(course_key)
    chapters = course.get_children()

    sequentials = []

    for chapter in chapters:
        sequentials += chapter.get_children()

    verticals = []

    for sequential in sequentials:
        verticals += sequential.get_children()

    allowed_block_types = stats_settings.get("API_XBLOCK_TYPES", [])
    components = {key: 0 for key in allowed_block_types}

    for vertical in verticals:
        for component in vertical.children:
            if component.block_type in allowed_block_types:
                components[component.block_type] = components.get(component.block_type, 0) + 1

    instructors = CourseAccessRole.objects.filter(course_id=course_key).values('user').distinct().count()
    learners = CourseEnrollment.objects.filter(
        course=course_key,
        user__is_staff=False,
        user__is_superuser=False
    ).values('user').distinct().count()

    return {
        "id": str(course_key),
        "name": course.display_name,
        "learners": learners,
        "instructors": instructors,
        "sections": len(chapters),
        "sub_sections": len(sequentials),
        "units": len(verticals),
        "components": components
    }


@cache_method
def get_learners_metric(tenant):
    """
    Returns the total of learners based on CourseEnrollments records.

    Args:
        tenant<str>: String tenant identifier(site.domain)

    Return:
        <int>: Total of learners.
    """
    tenant_courses = get_cached_courses(tenant)

    return CourseEnrollment.objects.filter(
        course__in=tenant_courses,
        user__is_staff=False,
        user__is_superuser=False,
    ).values('user').distinct().count()


@cache_method
def get_instructors_metric(tenant):  # pylint: disable=unused-argument
    """
    Returns the total of instructors based on the accessible orgs, and the CourseAccessRole records.

    Args:
        tenant<str>: This argument is used as identifier by the cache_method decorator.

    Return:
        <int>: Total of instructors.
    """
    current_site_orgs = configuration_helpers.get_current_site_orgs()

    return CourseAccessRole.objects.filter(org__in=current_site_orgs).values('user').distinct().count()


@cache_method
def get_courses_metrics(tenant):
    """
    Returns the total of courses and its metrics.

    Args:
        tenant<str>: String tenant identifier(site.domain)

    Return:
        <Dictionary>: Contains the courses' metrics.
    """
    courses = get_cached_courses(tenant)
    metrics = [get_course_metrics(course.id) for course in courses]

    return {"total_courses": courses.count(), "metrics": metrics}
