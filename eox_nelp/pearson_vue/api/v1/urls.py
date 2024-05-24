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

app_name = "eox_nelp"  # pylint: disable=invalid-name

urlpatterns = [
    path('resultNotification/', ResultNotificationView.as_view(), name='resultNotification'),
    path('placeHold/', PlaceHoldView.as_view(), name='placeHold'),
    path('releaseHold/', ReleaseHoldView.as_view(), name='releaseHold'),
    path('modifyResultStatus/', ModifyResultStatusView.as_view(), name='modifyResultStatus'),
    path('revokeResult/', RevokeResultView.as_view(), name='revokeResult'),
    path('unrevokeResult/', UnrevokeResultView.as_view(), name='unrevokeResult'),
]
