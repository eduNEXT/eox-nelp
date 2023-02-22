"""Test Backend module."""
from django.contrib import admin
from django.db import models
from rest_framework.views import APIView


def create_test_model(name, app_label='', module='', fields=None):
    """
    Create tests model.
    """
    class Meta:
        """Empty class used to generate test models."""

    if app_label:
        setattr(Meta, 'app_label', app_label)

    attrs = {'__module__': module, 'Meta': Meta}

    if fields:
        attrs.update(fields)

    return type(name, (models.Model,), attrs)


class DummyAdmin(admin.ModelAdmin):
    """Dummy admin model."""


class DummyView(APIView):
    """Dummy APIView class."""
