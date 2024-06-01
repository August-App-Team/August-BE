from rest_framework import serializers
from apps.users.models import User
from apps.users.serializers import ImageOrUrlField


class FriendSerializer(serializers.ModelSerializer):
    profile_image = ImageOrUrlField()
    department = serializers.CharField(source="department.nickname")

    class Meta:
        model = User
        fields = ["id", "name", "profile_image", "year_in_school", "department"]
        read_only_fields = fields