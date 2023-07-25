"""
This file contains all the processes that must run after app registration.

Functions:

    run_init_pipeline: Wrapper for all the init methods, this avoids to import methods outside this file.
    patch_user_gender_choices: Change the current openedx gender options (Male, Female, Other)

"""
from django.utils.translation import gettext_noop


def run_init_pipeline():
    """
    Executes multiple processes that must run before starting the django application.
    """
    patch_user_gender_choices()


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
