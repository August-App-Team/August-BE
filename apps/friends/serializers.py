from rest_framework import serializers
from apps.courses.serializers import InstitutionSerializer
from apps.users.models import User
from apps.users.serializers import ImageOrUrlField


class FriendSerializer(serializers.ModelSerializer):
    profile_image = ImageOrUrlField()
    department = serializers.SerializerMethodField()
    institution = InstitutionSerializer()

    class Meta:
        model = User
        fields = [
            "id",
            "name",
            "profile_image",
            "year_in_school",
            "department",
            "institution",
        ]
        read_only_fields = fields

    def get_department(self, obj):
        return obj.department.nickname if obj.department else None


class MeetingIntervalSerializer(serializers.Serializer):
    days = serializers.CharField()
    start_time = serializers.TimeField(format="%H:%M")
    end_time = serializers.TimeField(format="%H:%M")

    def to_representation(self, instance):
        return {"days": instance[0], "start_time": instance[1], "end_time": instance[2]}
