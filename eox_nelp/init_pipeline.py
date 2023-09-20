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
    from eox_nelp.course_experience.frontend import templates as course_experience_templates
    from eox_nelp.edxapp_wrapper.edxmako import edxmako
    from eox_nelp.stats import templates as stats_templates

    templates_modules_to_include = [
        stats_templates,
        course_experience_templates,
    ]

    for module in templates_modules_to_include:
        path_to_templates = os.path.dirname(module.__file__)

        if path_to_templates not in edxmako.LOOKUP['main'].directories:
            edxmako.paths.add_lookup('main', path_to_templates)
