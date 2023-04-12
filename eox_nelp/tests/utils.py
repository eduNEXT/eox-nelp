""" Module with methods to reuse in test cases"""
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
        else:
            setattr(model, key, value)
    return model
