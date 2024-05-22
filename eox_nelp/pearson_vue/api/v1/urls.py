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
