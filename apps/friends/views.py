from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from apps.friends.models import Friend
from django.db.models import Q
from django.contrib.auth import get_user_model

from apps.friends.serializers import FriendSerializer


class FriendListView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = FriendSerializer

    def get_queryset(self):
        user = self.request.user

        friends = Friend.objects.filter(Q(user1=user) | Q(user2=user)).values_list(
            "user1", "user2"
        )
        friend_ids = set(id for pair in friends for id in pair if id != user.id)
        return get_user_model().objects.filter(id__in=friend_ids)
