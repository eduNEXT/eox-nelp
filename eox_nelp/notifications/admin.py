"""Notifications admin file.

Contains the admin models for notifications.

classes:
    DueDateListFilter: Admin class for LikeDislikeUnit model.
    UpcomingCourseDueDateAdmin: Admin class for UpcomingCourseDueDate model.

functions:
    notify_due_dates: It will call notify method for every queryset record,
                      this only works with UpcomingCourseDueDate models.
"""
import datetime

from django.contrib import admin
from django.contrib.admin import DateFieldListFilter
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from eox_nelp.notifications.models import UpcomingCourseDueDate


class DueDateListFilter(DateFieldListFilter):
    """Filter class that allows to filter by upcoming dates.

    The filter action will be applied from the current day until the specified parameter,
    the options are the following:

        1) Any date: it won't apply any filter.
        2) Next day: Records from now until 1 day in the future.
        3) Next seven days: Records from now until 7 days in the future.
        4) Next month: Records from now until 30 days in the future.
    """
    # pylint: disable=too-many-arguments, too-many-positional-arguments

    def __init__(self, field, request, params, model, model_admin, field_path):
        """Custom init method to modify inherited options"""
        super().__init__(field, request, params, model, model_admin, field_path)
        today = timezone.now()

        self.links = (
            (_("Any date"), {}),
            (
                _("Next day"),
                {
                    self.lookup_kwarg_since: today,
                    self.lookup_kwarg_until: today + datetime.timedelta(days=1),
                },
            ),
            (
                _("Next seven days"),
                {
                    self.lookup_kwarg_since: today,
                    self.lookup_kwarg_until: today + datetime.timedelta(days=7),
                },
            ),
            (
                _("Next month"),
                {
                    self.lookup_kwarg_since: today,
                    self.lookup_kwarg_until: today + datetime.timedelta(days=30),
                },
            ),
        )


@admin.action(description="Send selected notifications")
def notify_due_dates(model_admin, request, queryset):  # pylint: disable=unused-argument
    """Notify due dates to enrolled users.

    Arguments:
        model_admin: UpcomingCourseDueDateAdmin instance.
        request: Current request.
        queryset: List of selected UpcomingCourseDueDate records.
    """
    for instance in queryset:
        instance.notify()


class UpcomingCourseDueDateAdmin(admin.ModelAdmin):
    """Admin class for UpcomingCourseDueDate.

    Attributes:
        list_display: Fields to be shown in admin interface.
        search_fields: Allow searching by these fields.
        actions: Bulk custom actions.
        list_filter: Allow filtering by these fields.
    """
    raw_id_fields = ["course"]
    list_display = ("course", "location_id", "notification_date", "due_date", "sent")
    search_fields = ("course__id", "location_id")
    actions = [notify_due_dates]
    list_filter = (
        "sent",
        ("due_date", DueDateListFilter),
        ("notification_date", DueDateListFilter),
    )


admin.site.register(UpcomingCourseDueDate, UpcomingCourseDueDateAdmin)
