"""
Constants for xAPI specifications, this contains the NELC required values.
"""
from eox_nelp.course_experience.models import RATING_OPTIONS

DEFAULT_LANGUAGE = "en-US"
RATED = "rated"
MAX_FEEDBACK_SCORE = RATING_OPTIONS[-1][0]
MIN_FEEDBACK_SCORE = 0

XAPI_ACTIVITY_COURSE = "https://w3id.org/xapi/cmi5/activitytype/course"
XAPI_ACTIVITY_UNIT_TEST = "http://id.tincanapi.com/activitytype/unit-test"

XAPI_VERB_RATED = "http://id.tincanapi.com/verb/rated"
