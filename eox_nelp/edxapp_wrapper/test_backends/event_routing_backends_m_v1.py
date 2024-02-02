"""Backend for event-routing-backends library.

This is required since the library has explicit dependencies from openedx platform.
https://github.com/openedx/event-routing-backends
"""
from mock import Mock


def get_xapi_constants():
    """Test backend for the constants module.

    Returns:
        Mock class.
    """
    constants = Mock()
    constants.EN = "en"
    constants.XAPI_VERB_INITIALIZED = "http://adlnet.gov/expapi/verbs/initialized"
    constants.XAPI_ACTIVITY_COURSE = "http://adlnet.gov/expapi/activities/course"
    constants.INITIALIZED = "initialized"
    constants.XAPI_ACTIVITY_MODULE = "http://adlnet.gov/expapi/activities/module"
    constants.XAPI_ACTIVITY_QUESTION = "http://adlnet.gov/expapi/activities/question"
    constants.XAPI_VERB_ATTEMPTED = "http://adlnet.gov/expapi/verbs/attempted"
    constants.ATTEMPTED = "attempted"

    return constants


def get_xapi_transformer_registry():
    """Test backend for the XApiTransformersRegistry class.

    Returns:
        Mock class.
    """
    XApiTransformersRegistry = Mock()
    XApiTransformersRegistry.register.return_value = lambda x: x

    return XApiTransformersRegistry


def get_xapi_transformer():
    """Test backend for the XApiTransformer class.

    Returns:
        Object type.
    """
    class XApiTransformer:
        pass

    setattr(XApiTransformer, "get_data", Mock())
    setattr(XApiTransformer, "get_object_iri", Mock())

    return XApiTransformer


def get_xapi_event_transformers():
    """Test backend for the event_transformers module.

    Returns:
        Mock class.
    """
    class ProblemSubmittedTransformer:
        pass

    setattr(ProblemSubmittedTransformer, "get_data", Mock())
    setattr(ProblemSubmittedTransformer, "get_object_iri", Mock())

    return Mock(
        ProblemSubmittedTransformer=ProblemSubmittedTransformer
    )
