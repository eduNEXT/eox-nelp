"""Custom NELP  authentication Exceptions
"""


class EoxNelpAuthException(ValueError):
    """Auth process exception.
    Inspired in https://github.com/eduNEXT/eox-tenant/blob/master/eox_tenant/pipeline.py#L6
    """

    def __init__(self, backend, *args, **kwargs):
        self.backend = backend
        super().__init__(*args, **kwargs)
