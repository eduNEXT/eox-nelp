"""
URL configuration for Pearson VUE API views.

This module defines the URL patterns for the Pearson VUE API endpoints.
Each endpoint corresponds to a specific view that handles a particular
type of event related to Pearson VUE.

URL Patterns:
    - resultNotification: Endpoint for handling result notifications.
    - placeHold: Endpoint for placing a hold.
    - releaseHold: Endpoint for releasing a hold.
    - modifyResultStatus: Endpoint for modifying the result status.
    - revokeResult: Endpoint for revoking a result.
    - unrevokeResult: Endpoint for unrevoking a result.
"""
from rest_framework.routers import DefaultRouter

from eox_nelp.pearson_vue.api.v1.views import (
    CancelAppointmentView,
    ModifyAppointmentView,
    ModifyResultStatusView,
    PlaceHoldView,
    ReleaseHoldView,
    ResultNotificationView,
    RevokeResultView,
    UnrevokeResultView,
)
from eox_nelp.pearson_vue.constants import (
    CANCEL_APPOINTMENT,
    MODIFY_APPOINTMENT,
    MODIFY_RESULT_STATUS,
    PLACE_HOLD,
    RELEASE_HOLD,
    RESULT_NOTIFICATION,
    REVOKE_RESULT,
    UNREVOKE_RESULT,
)

app_name = "eox_nelp"  # pylint: disable=invalid-name

router = DefaultRouter()
router.register('resultNotification', ResultNotificationView, basename=RESULT_NOTIFICATION)
router.register('placeHold', PlaceHoldView, basename=PLACE_HOLD)
router.register('releaseHold', ReleaseHoldView, basename=RELEASE_HOLD)
router.register('modifyResultStatus', ModifyResultStatusView, basename=MODIFY_RESULT_STATUS)
router.register('revokeResult', RevokeResultView, basename=REVOKE_RESULT)
router.register('unrevokeResult', UnrevokeResultView, basename=UNREVOKE_RESULT)
router.register('modifyAppointment', ModifyAppointmentView, basename=MODIFY_APPOINTMENT)
router.register('cancelAppointment', CancelAppointmentView, basename=CANCEL_APPOINTMENT)

urlpatterns = router.urls
