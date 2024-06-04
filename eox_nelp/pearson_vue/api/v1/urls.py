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
from django.urls import path

from eox_nelp.pearson_vue.api.v1.views import (
    ModifyResultStatusView,
    PlaceHoldView,
    ReleaseHoldView,
    ResultNotificationView,
    RevokeResultView,
    UnrevokeResultView,
)
from eox_nelp.pearson_vue.constants import (
    MODIFY_RESULT_STATUS,
    PLACE_HOLD,
    RELEASE_HOLD,
    RESULT_NOTIFICATION,
    REVOKE_RESULT,
    UNREVOKE_RESULT,
)

app_name = "eox_nelp"  # pylint: disable=invalid-name

urlpatterns = [
    path('resultNotification/', ResultNotificationView.as_view(), name=RESULT_NOTIFICATION),
    path('placeHold/', PlaceHoldView.as_view(), name=PLACE_HOLD),
    path('releaseHold/', ReleaseHoldView.as_view(), name=RELEASE_HOLD),
    path('modifyResultStatus/', ModifyResultStatusView.as_view(), name=MODIFY_RESULT_STATUS),
    path('revokeResult/', RevokeResultView.as_view(), name=REVOKE_RESULT),
    path('unrevokeResult/', UnrevokeResultView.as_view(), name=UNREVOKE_RESULT),
]
