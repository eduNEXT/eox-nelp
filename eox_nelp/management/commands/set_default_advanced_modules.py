"""
Management command to enqueue the `set_default_advanced_modules` task for one or all courses.

This command is used to update the `advanced_modules` list in the modulestore
based on organization-level defaults. It can operate on a specific course
(using `--course-id`) or all available courses (`--all`).
"""
import logging

from django.core.management.base import BaseCommand, CommandError

from eox_nelp.edxapp_wrapper.course_overviews import CourseOverview
from eox_nelp.edxapp_wrapper.modulestore import ModuleStoreEnum
from eox_nelp.signals.tasks import set_default_advanced_modules

DEFAULT_USER_ID = ModuleStoreEnum.UserID.mgmt_command
logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Enqueues the `set_default_advanced_modules` task for a specific course or all courses.

    Examples:
        # Run for all courses
        python manage.py cms set_default_advanced_modules --all

        # Run for a single course
        python manage.py cms set_default_advanced_modules --course-id course-v1:ORG+CODE+RUN
    """

    help = "Set default advanced modules for a course or all courses"

    def add_arguments(self, parser):
        parser.add_argument(
            "--all",
            action="store_true",
            help="Apply to all CourseOverview records",
        )
        parser.add_argument(
            "--course-id",
            type=str,
            help="Specific course_id to apply the task to",
        )

    def handle(self, *args, **options):
        if options["all"]:
            courses = CourseOverview.objects.all()
            logger.info("Processing %s courses...", courses.count())
            for course in courses:
                set_default_advanced_modules.delay(
                    user_id=DEFAULT_USER_ID,
                    course_id=str(course.id)
                )
                logger.info("Queued task for %s", course.id)
        else:
            course_id = options.get("course_id")
            if not course_id:
                raise CommandError("You must provide --course-id unless using --all")
            try:
                course = CourseOverview.objects.get(id=course_id)
            except CourseOverview.DoesNotExist as exc:
                raise CommandError(f"CourseOverview with id '{course_id}' not found.") from exc

            set_default_advanced_modules.delay(
                user_id=DEFAULT_USER_ID,
                course_id=str(course.id)
            )
            logger.info("Queued task for %s", course.id)
