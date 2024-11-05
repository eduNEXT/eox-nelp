"""General admin module file.
Register all the nelp admin models.
"""
from importlib.util import find_spec

from django.conf import settings

from eox_nelp.admin.certificates import *  # noqa: F401
from eox_nelp.admin.course_creators import *  # noqa: F401
from eox_nelp.admin.student import *  # noqa: F401
from eox_nelp.course_experience.admin import *  # noqa: F401
from eox_nelp.notifications.admin import *  # noqa: F401
from eox_nelp.payment_notifications.admin import *  # noqa: F401
from eox_nelp.pearson_vue.admin import *  # noqa: F401

if find_spec('eox_support') and 'eox_support.apps.EoxSupportConfig' in settings.INSTALLED_APPS:
    from eox_nelp.admin.user import *  # noqa: F401
