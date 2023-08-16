"""Utils that can be used for the plugin project"""
import re
from copy import copy

NATIONAL_ID_REGEX = r"^[1-2]\d{9}$"


def map_instance_attributes_to_dict(instance, attributes_mapping):
    """Create a dictionary that represents some fields or attributes of a instance based on
    a attributes_mapping dictionary. This dict would have key, values which the key represent the
    attribute to look in the instance and the value the key name in the output dict.
    Based in the `attributes_mapping` you should use a dict with the following config:
    {
        "key_name": "field_name"
    }
    This would check in the instace instance.field_name and the value send it to output dict
    like {"key_name": instance.field_name}
    Also its is possible to check nested fields if you declarate the field of instance separated by `__`
    eg:
    {
        "key_name": "field_level1__field_level2"
    }
    This example would check in the instace like instance.field_level1.field_level2 and in the output
    dict like {"key_name": instance.field_level1.field_level2}
    Args:
        instance (instance class): Model or instance of class to retrieved fields.
        attributes_mapping (dict): Dictionary map that has the fields to search and the keys name to output,

    Returns:
        instance_dict: dict representing the instance
    """
    instance_dict = {}
    for extra_field, instance_field in attributes_mapping.items():
        extra_value = None
        instance_level = copy(instance)
        for instance_field in instance_field.split("__"):
            if hasattr(instance_level, instance_field):
                instance_level = getattr(instance_level, instance_field)
                extra_value = instance_level

        instance_dict[extra_field] = extra_value

    return instance_dict


def check_regex(string, regex):
    """Checks if the string matches the regex.

    Args:
        string: The string to check.
        regex: The regex to match against.

    Returns:
        True if the string matches the regex, False otherwise.
    """
    pattern = re.compile(regex)

    return pattern.match(string) is not None


def is_valid_national_id(national_id, raise_exception=False):
    """Validate if a national_id has the shape of a national_id

    Args:
        national_id: The string of national_id to check.

    Returns:
        True if the national_id is ok, False otherwise.

    Raise:
    ValueError: This will be raised when the username are excluded dont match national Id regex.
    """
    check_national_id = check_regex(national_id, NATIONAL_ID_REGEX)

    if raise_exception and not check_national_id:
        raise ValueError(
            f"The username or national_id: {national_id} doesnt match national ID regex ({NATIONAL_ID_REGEX})",
        )

    return check_national_id
