"""Module to add validators related Pearson Vue Integration"""

import logging

from pydantic import ValidationError

from eox_nelp.pearson_vue.data_classes import CddRequest, EadRequest

try:
    from eox_audit_model.decorators import audit_method
except ImportError:
    def audit_method(action):  # pylint: disable=unused-argument
        """Identity audit_method"""
        return lambda x: x


logger = logging.getLogger(__name__)


def validate_cdd_request(cdd_request):
    """
    Validates an CDD request dictionary using a Pydantic model.

    This function attempts to create a Pydantic model instance (likely named `class CddRequest`:
`)
    from the provided `cdd_request` dictionary. It performs data validation based on the
    model's data type definitions.
    Then if there is an error then that error is raised using audit. audit_validation_error

    Args:
        cdd_request (dict): The dictionary containing the EAD request data.
    """
    try:
        CddRequest(**cdd_request)
    except ValidationError as validation_exception:
        logger.info("Validation error for cdd_request: %s \n %s", cdd_request, validation_exception)
        audit_validation_error(validation_exception.json(), cdd_request=cdd_request)

    logger.info("Valid values for cdd_request: \n @clientCandidateID: %s", cdd_request["@clientCandidateID"])


def validate_ead_request(ead_request):
    """
    Validates an EAD request dictionary using a Pydantic model.

    This function attempts to create a Pydantic model instance (likely named `EadRequest`)
    from the provided `ead_request` dictionary. It performs data validation based on the
    model's data type definitions.
    Then if there is an error then that error is raised using audit. audit_validation_error

    Args:
        ead_request (dict): The dictionary containing the EAD request data.
    """
    try:
        EadRequest(**ead_request)
    except ValidationError as validation_exception:
        logger.info("Validation error for ead_request: %s \n %s", ead_request, validation_exception)
        audit_validation_error(validation_exception.json(), ead_request=ead_request)
    logger.info("Valid values for ead_request: \n @clientAuthorizationID: %s", ead_request["@clientAuthorizationID"])


@audit_method(action="PearsonVue Error validating data")
def audit_validation_error(*args, **kwargs):
    """
    Method to raise an error with eox-audit
    Args:
        validation_exception: exception to be raised.
    Raises:
        ValueError: Value error with args info.
    """
    raise ValueError(*args)
