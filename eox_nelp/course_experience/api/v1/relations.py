"""Relations used for customize experience views. The relations are used to specify how to manage
the relations fields in the serializers.
https://github.com/encode/django-rest-framework/blob/master/rest_framework/relations.py
"""
from rest_framework_json_api.relations import ResourceRelatedField


class ExperienceResourceRelatedField(ResourceRelatedField):
    """Class to configure relations for course experience API.

    Ancestors:
        relation (ResourceRelatedField): the ResourceRelatedField relation from json api

    """
    def __init__(self, **kwargs):
        """ Include an additional kwargs parameter to manage the extra model fields to be shown.
        The value of the kwarg should be  a function with kwargs accepting value: (value=instance).
        get_extra_fields (function)
        """
        self.get_extra_fields = kwargs.pop('get_extra_fields', None)
        super().__init__(**kwargs)

    def to_representation(self, value):
        """Add to the base json api representation extra fields apart from `id` and `type`
        using a function passed via `self.get_extra_fields`
        https://github.com/django-json-api/django-rest-framework-json-api/blob/main/rest_framework_json_api/relations.py#L255
        The attributes shape is based on
        https://jsonapi.org/format/#document-resource-objects
        Args:
            value (instance model): instance of foreign model extracted from relation

        Returns:
           json_api_representation (ordered-dict): json api representation with extra model data in attributes field.
        """
        json_api_representation = super().to_representation(value)

        if self.get_extra_fields and callable(self.get_extra_fields):
            json_api_representation.update(self.get_extra_fields(value=value))

        return json_api_representation
