"""General method to register admin models.
methods:
    register_admin_model: Force register admin model.
"""
from django.apps import apps
from django.contrib import admin


def register_admin_model(model, admin_model):
    """Associate a model with the given admin model.
    Args:
        model: Django model.
        admin_class: Admin model.
    """
    try:
        apps.get_app_config(model._meta.app_label)  # pylint: disable=protected-access
    except LookupError:
        return

    if admin.site.is_registered(model):
        admin.site.unregister(model)

    admin.site.register(model, admin_model)
