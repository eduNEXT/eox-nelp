"""
This module defines the Django admin configuration for handling user model.

Classes:
    NelpUserAdmin: Custom admin class for User model to include extra info fields like national_id.
    UserExtraInfoInline: inline for extra info model
"""
from custom_reg_form.models import ExtraInfo
from django.contrib import admin, messages
from django.contrib.admin import StackedInline
from django.contrib.auth import get_user_model
from django.utils import timezone
from eox_support.admin.user import SupportUserAdmin  # pylint: disable=import-error

from eox_nelp.admin.register_admin_model import register_admin_model as register
from eox_nelp.edxapp_wrapper.django_comment_common import comment_client
from eox_nelp.edxapp_wrapper.user_api import accounts, models

User = get_user_model()


class UserExtraInfoInline(StackedInline):
    """ Inline admin interface for Extra Info model. """
    model = ExtraInfo
    can_delete = False
    verbose_name_plural = 'Extra info'


class NelpUserAdmin(SupportUserAdmin):
    """EoxNelp User admin class."""
    list_display = SupportUserAdmin.list_display[:2] + ('user_national_id',) + SupportUserAdmin.list_display[2:]
    search_fields = SupportUserAdmin.search_fields + ('extrainfo__national_id',)
    inlines = SupportUserAdmin.inlines + (UserExtraInfoInline,)
    actions = ['retire_users']

    def user_national_id(self, instance):
        """Return national_id associated with the user extra_info instance."""
        if getattr(instance, "extrainfo", None):
            return instance.extrainfo.national_id

        return None

    @admin.action(description="Retire selected users")
    def retire_users(self, request, queryset):
        """
        Admin action to retire selected users from the Django admin interface.

        This action performs the following steps for each selected user:
        - Appends a unique timestamp-based label to the user's email and username to mark retirement.
        - Saves the updated user object to persist the new identifiers.
        - Creates a retirement request and deactivates the user account.
        - Deletes any associated ExtraInfo records.
        - Attempts to retire the user from the external comment/forum service.

        If the user has already been retired, a RetirementStateError is caught and an error message is shown.
        If the user does not exist in the comment service, a 404 is caught and a message is shown.
        Any other unexpected exceptions are logged as errors in the admin interface.

        Args:
            request: The HttpRequest object.
            queryset: A QuerySet of selected User instances to retire.
        """
        timestamp = int(timezone.now().timestamp())
        label = f"-retired-by-{request.user.username}-{timestamp}"

        for user in queryset:
            try:
                cc_user = comment_client.User.from_django_user(user)
                user.email += label
                user.username += label
                user.save()
                accounts.utils.create_retirement_request_and_deactivate_account(user)
                ExtraInfo.objects.filter(user=user).delete()  # pylint: disable=no-member
                cc_user.retire(user.username)
            except models.RetirementStateError:
                messages.error(request, f"User retirement already exist for user with id {user.id}")
            except comment_client.CommentClientRequestError as exc:
                if exc.status_code != 404:
                    raise
                messages.error(request, f"User with id {user.id} not found in forum service")
            except Exception as exc:  # pylint: disable=broad-except
                messages.error(request, f"Error during soft delete process for user ID {user.id}: {str(exc)}")


register(User, NelpUserAdmin)
