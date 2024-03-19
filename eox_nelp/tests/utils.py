""" Module with methods to reuse in test cases"""
import datetime

from django.core.cache import cache
from mock import Mock


def generate_list_mock_data(data):
    """Helper method to create Mock subsection based on the given data.
    You can use it to generate queryset or models.
    Inspired in https://github.com/eduNEXT/eox-nelp/blob/master/eox_nelp/notifications/tests/test_tasks.py#L345
    Args:
        data: This should be a list of dicts with the following structure:
    [
        {
            "due" : "due_date",
            "location": "location",
            "user": {
                "email": "bruce@gmail.com"
            }
        },
        {
            "due": "due_date",
            "location": "location"
        },
        {
            "due" : "due_date",
            "components": [
                {
                    "block_type": "problem",
                },
                {
                    "block_type": "video",
                },
                {
                    "block_type": "html",
                },
            ]
        },
    ]

    Every dictionary should be direct key values.No way if there is nested dict the model
    would be nested.
    for example for element 0, in the response you could access to the mock qs[0].user.email
    and retrieve
    Returns:
        List of mocks.
    """
    list_mock = []
    for element in data:
        model = set_key_values(element)
        list_mock.append(model)

    return list_mock


def set_key_values(element):
    """Method to set key values nested. So is based in recursive dicts"""
    model = Mock()
    for key, value in element.items():
        if isinstance(value, dict):
            setattr(model, key, set_key_values(value))
        elif isinstance(value, list):
            setattr(model, key, generate_list_mock_data(value))
        else:
            setattr(model, key, value)
    return model


def get_cache_expiration_time(key):
    """
    Util to get the expiration time of a key cache in seconds.
    Args:
        key <str>: Cache key to be searched in cache.
    Returns:
        int: expiration remaining time of the key in seconds. If there is a problem with the key time return 0.
    """
    # use make_key to generate Django's internal key storage name
    expiration_unix_timestamp = cache._expire_info.get(cache.make_key(key))  # pylint: disable=protected-access
    if expiration_unix_timestamp is None:
        return 0

    expiration_date_time = datetime.datetime.fromtimestamp(expiration_unix_timestamp)
    now = datetime.datetime.now()

    # Be careful subtracting an older date from a newer date does not give zero
    if expiration_date_time < now:
        return 0

    # give me the seconds left till the key expires
    delta = expiration_date_time - now
    return delta.seconds
