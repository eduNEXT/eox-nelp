from rest_framework import serializers

from eox_nelp.pearson_vue.models import PearsonRTENModel


class PearsonRTENSerializer(serializers.ModelSerializer):

    content = serializers.JSONField()

    class Meta:
        model = PearsonRTENModel
        fields = ["event_type", "content", "created_at"]
        read_only_fields = ["event_type", "created_at"]

    def to_internal_value(self, data):
        return {"content": data}
