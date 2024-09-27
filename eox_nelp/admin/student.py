"""
This module defines the Django admin configuration for handling student models.

Classes:
    NelpCourseEnrollmentAdmin: Custom admin class for CourseEnrollment model to include Pearson RTI action.

Functions:
    pearson_real_time_action(modeladmin, request, queryset): Admin action to execute Pearson RTI request
        for selected course enrollments.
    pearson_add_ead_action(modeladmin, request, queryset): Admin action to execute Pearson add EAD request
        for selected course enrollments.
    pearson_update_ead_action(modeladmin, request, queryset): Admin action to execute Pearson update EAD request
        for selected course enrollments.
    pearson_delete_ead_action(modeladmin, request, queryset): Admin action to execute Pearson delete EAD request
        for selected course enrollments.
    pearson_cdd_action(modeladmin, request, queryset): Admin action to execute Pearson CDD request
        for selected course enrollments.
"""

import logging

from django.conf import settings
from django.contrib import admin

from eox_nelp.admin.register_admin_model import register_admin_model as register
from eox_nelp.edxapp_wrapper.student import CourseEnrollment, CourseEnrollmentAdmin
from eox_nelp.pearson_vue.tasks import real_time_import_task_v2

logger = logging.getLogger(__name__)


@admin.action(description="Execute Pearson RTI request")
def pearson_real_time_action(modeladmin, request, queryset):  # pylint: disable=unused-argument
    """
    Admin action to execute Pearson RTI request for selected course enrollments.

    This function iterates over the selected course enrollments and initiates the
    real-time import task for each enrollment.

    Args:
        modeladmin: The current ModelAdmin instance.
        request: The current HttpRequest instance.
        queryset: The QuerySet of selected CourseEnrollment instances.
    """
    for course_enrollment in queryset:
        logger.info(
            "Initializing rti task for the user %s, action triggered by admin action",
            course_enrollment.user.id,
        )
        real_time_import_task_v2.delay(
            user_id=course_enrollment.user.id,
            exam_id=str(course_enrollment.course_id),
            action_name="rti",
        )


@admin.action(description="Execute Pearson EAD Add request")
def pearson_add_ead_action(modeladmin, request, queryset):  # pylint: disable=unused-argument
    """
    Admin action to execute Pearson EAD Add request for selected course enrollments.

    This function iterates over the selected course enrollments and initiates the
    add ead_task for each enrollment.

    Args:
        modeladmin: The current ModelAdmin instance.
        request: The current HttpRequest instance.
        queryset: The QuerySet of selected CourseEnrollment instances.
    """
    for course_enrollment in queryset:
        logger.info(
            "Initializing ead add task for the user %s, action triggered by admin action",
            course_enrollment.user.id,
        )
        real_time_import_task_v2.delay(
            user_id=course_enrollment.user.id,
            exam_id=str(course_enrollment.course_id),
            action_name="ead",
            transaction_type="Add",
        )


@admin.action(description="Execute Pearson EAD Update request")
def pearson_update_ead_action(modeladmin, request, queryset):  # pylint: disable=unused-argument
    """
    Admin action to execute Pearson EAD Update request for selected course enrollments.

    This function iterates over the selected course enrollments and initiates the
    update ead_task for each enrollment.

    Args:
        modeladmin: The current ModelAdmin instance.
        request: The current HttpRequest instance.
        queryset: The QuerySet of selected CourseEnrollment instances.
    """
    for course_enrollment in queryset:
        logger.info(
            "Initializing ead update task for the user %s, action triggered by admin action",
            course_enrollment.user.id,
        )
        real_time_import_task_v2.delay(
            user_id=course_enrollment.user.id,
            exam_id=str(course_enrollment.course_id),
            action_name="ead",
            transaction_type="Update",
        )


@admin.action(description="Execute Pearson EAD Delete request")
def pearson_delete_ead_action(modeladmin, request, queryset):  # pylint: disable=unused-argument
    """
    Admin action to execute Pearson EAD Delete request for selected course enrollments.

    This function iterates over the selected course enrollments and initiates the
    delete ead_task for each enrollment.

    Args:
        modeladmin: The current ModelAdmin instance.
        request: The current HttpRequest instance.
        queryset: The QuerySet of selected CourseEnrollment instances.
    """
    for course_enrollment in queryset:
        logger.info(
            "Initializing ead delete task for the user %s, action triggered by admin action",
            course_enrollment.user.id,
        )
        real_time_import_task_v2.delay(
            user_id=course_enrollment.user.id,
            exam_id=str(course_enrollment.course_id),
            action_name="ead",
            transaction_type="Delete",
        )


@admin.action(description="Execute Pearson CDD request for student.")
def pearson_cdd_action(modeladmin, request, queryset):  # pylint: disable=unused-argument
    """
    Admin action to execute Pearson CDD request for selected course enrollments.

    This function iterates over the selected course enrollments and initiates the
    cdd_task for each enrollment.

    Args:
        modeladmin: The current ModelAdmin instance.
        request: The current HttpRequest instance.
        queryset: The QuerySet of selected CourseEnrollment instances.
    """
    for course_enrollment in queryset:
        logger.info(
            "Initializing cdd task for the user %s, action triggered by admin action",
            course_enrollment.user.id,
        )
        real_time_import_task_v2.delay(
            user_id=course_enrollment.user.id,
            action_name="cdd",
        )


class NelpCourseEnrollmentAdmin(CourseEnrollmentAdmin):
    """
    Custom admin class for CourseEnrollment model to include Pearson RTI action.

    This class extends the CourseEnrollmentAdmin and adds the custom admin action
    `pearson_real_time_action` to the list of available actions in the admin interface.
    """
    @property
    def actions(self):
        """
        Actions property that returns specific actions if the USE_PEARSON_ENGINE_SERVICE setting
        has been configured.
        """
        if getattr(settings, "USE_PEARSON_ENGINE_SERVICE", False):
            return [
                pearson_real_time_action,
                pearson_add_ead_action,
                pearson_update_ead_action,
                pearson_delete_ead_action,
                pearson_cdd_action,
            ]

        return []


register(CourseEnrollment, NelpCourseEnrollmentAdmin)
