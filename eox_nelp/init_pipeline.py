"""
This file contains all the processes that must run after app registration.

Functions:

    run_init_pipeline: Wrapper for all the init methods, this avoids to import methods outside this file.
    patch_user_gender_choices: Change the current openedx gender options (Male, Female, Other)

"""
import os

from django.utils.translation import gettext_noop


def run_init_pipeline():
    """
    Executes multiple processes that must run before starting the django application.
    """
    patch_user_gender_choices()
    set_mako_templates()
    register_xapi_transformers()
    update_permissions()
    patch_generate_password()
    patch_registration_form_factory()


def patch_user_gender_choices():
    """
    This overwrites the available gender choices in order to allow the Male and Female options.
    """
    # pylint: disable=import-error, import-outside-toplevel
    # This cannot be at the top of the file since this file is imported the plugin initialization
    # and therefore the settings has not been set yet
    from eox_nelp.edxapp_wrapper.student import UserProfile

    UserProfile.GENDER_CHOICES = (
        ('m', gettext_noop('Male')),
        ('f', gettext_noop('Female')),
    )


def set_mako_templates():
    """This method adds the plugin templates to mako configuration."""
    # pylint: disable=import-error, import-outside-toplevel
    # This cannot be at the top of the file since this file is imported the plugin initialization
    # and therefore the settings has not been set yet
    from eox_nelp import static as templates
    from eox_nelp.edxapp_wrapper.edxmako import edxmako
    from eox_nelp.payment_notifications import templates as payment_notifications_templates
    from eox_nelp.phone_validation import templates as phone_validation_templates

    module_templates_to_include = [
        templates,
        payment_notifications_templates,
        phone_validation_templates,
    ]

    for module in module_templates_to_include:
        path_to_templates = os.path.dirname(module.__file__)

        if path_to_templates not in edxmako.LOOKUP['main'].directories:
            edxmako.paths.add_lookup('main', path_to_templates)


def register_xapi_transformers():
    """This method just import the event transformers in order to register all of them."""
    # pylint: disable=import-outside-toplevel, unused-import
    from eox_nelp.processors.xapi import event_transformers as xapi_event_transformers  # noqa: F401


def update_permissions():
    """This method just change permissions for bussiness cases"""
    # pylint: disable=import-outside-toplevel,unsupported-binary-operation
    from bridgekeeper import perms
    from bridgekeeper.rules import is_staff

    from eox_nelp.edxapp_wrapper.courseware import rules
    from eox_nelp.edxapp_wrapper.instructor import permissions

    perms.pop(permissions.CAN_RESEARCH, None)
    perms[permissions.CAN_RESEARCH] = (
        is_staff
        | rules.HasRolesRule("data_researcher")
        | rules.HasAccessRule("staff")
        | rules.HasAccessRule("instructor")
    )


def patch_generate_password():
    """This method patch `generate_password` of edx_django_util package,
    with custom nelp `generate_password`.
    """
    # pylint: disable=import-outside-toplevel, unused-import
    from edx_django_utils import user

    from eox_nelp.user_authn.utils import generate_password
    user.generate_password = generate_password


def patch_registration_form_factory():
    """This method patches `RegistrationFormFactory` of user_auth.view.registration_form ,
    with custom nelp `NelpRegistrationFormFactory`.
    """
    # pylint: disable=import-outside-toplevel, unused-import
    from eox_nelp.edxapp_wrapper.user_authn import views
    from eox_nelp.user_authn.views.registration_form import NelpRegistrationFormFactory
    views.registration_form.RegistrationFormFactory = NelpRegistrationFormFactory
