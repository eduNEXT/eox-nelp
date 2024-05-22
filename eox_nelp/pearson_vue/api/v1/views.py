from edx_rest_framework_extensions.auth.jwt.authentication import JwtAuthentication
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from eox_nelp.pearson_vue.api.v1.serializers import PearsonRTENSerializer
from eox_nelp.pearson_vue.models import PearsonRTENModel


class PearsonRTENBaseView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PearsonRTENSerializer
    queryset = PearsonRTENModel.objects.all()
    authentication_classes = [JwtAuthentication]

    def perform_create(self, serializer):
        content_data = self.request.data.copy()
        serializer.save(event_type=self.event_type, content=content_data)


class ResultNotificationView(PearsonRTENBaseView):
    event_type = "resultNotification"


class PlaceHoldView(PearsonRTENBaseView):
    event_type = "placeHold"


class ReleaseHoldView(PearsonRTENBaseView):
    event_type = "releaseHold"


class ModifyResultStatusView(PearsonRTENBaseView):
    event_type = "modifyResultStatus"


class RevokeResultView(PearsonRTENBaseView):
    event_type = "revokeResult"


class UnrevokeResultView(PearsonRTENBaseView):
    event_type = "unrevokeResult"
