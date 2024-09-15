from datetime import datetime, date
from django.conf import settings
from django.db.models import Q
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import status
from rest_framework.generics import ListAPIView, RetrieveAPIView, DestroyAPIView
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.friends.models import Friend, FriendCode
from apps.friends.serializers import FriendSerializer, MeetingIntervalSerializer
from apps.friends.utils import (
    get_hangout_intervals_of_users,
    get_random_code,
    is_valid_code,
)
from apps.timetables.models import TimeTable
from apps.timetables.serializers import TimeTableSerializer
from rest_framework.exceptions import NotFound, PermissionDenied


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


class FriendDeleteView(DestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = FriendSerializer

    def get_object(self):
        user = self.request.user
        friend_id = self.kwargs["friend_id"]

        friend = Friend.objects.filter(
            Q(user1=user, user2=friend_id) | Q(user1=friend_id, user2=user)
        ).first()
        if friend is not None:
            return friend
        else:
            raise NotFound("Not a friend or invalid friend_id.")

    def delete(self, request, *args, **kwargs):
        try:
            return super().destroy(request, *args, **kwargs)
        except NotFound as e:
            return Response(status=status.HTTP_404_NOT_FOUND)


class FriendTimeTableSemesterList(ListAPIView):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        friend_id = self.kwargs["friend_id"]

        if Friend.objects.filter(
            Q(user1=user, user2=friend_id) | Q(user1=friend_id, user2=user)
        ).exists():
            return (
                TimeTable.objects.filter(user=friend_id)
                .values_list("semester", flat=True)
                .distinct()
            )
        else:
            raise PermissionDenied("Access only allowed to friend.")

    def list(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            semester_codes = list(queryset.values_list("semester__code", flat=True))
            return Response(semester_codes)
        except PermissionDenied as e:
            return Response({"detail": str(e)}, status=status.HTTP_403_FORBIDDEN)


class FriendTimeTableView(RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TimeTableSerializer

    def get_object(self):
        user = self.request.user
        friend_id = self.kwargs["friend_id"]
        semester = self.kwargs["semester"]

        if Friend.objects.filter(
            Q(user1=user, user2=friend_id) | Q(user1=friend_id, user2=user)
        ).exists():
            # user and friend_id are friends

            try:
                return TimeTable.objects.get(
                    user=friend_id, semester__code=semester, order=0
                )
            except TimeTable.DoesNotExist:
                raise NotFound("No timetable exists for given user and semester.")
        else:
            raise PermissionDenied("Access only allowed to friend.")

    def get(self, request, *args, **kwargs):
        try:
            return super().retrieve(request, *args, **kwargs)
        except NotFound as e:
            return Response({"detail": str(e)}, status=status.HTTP_404_NOT_FOUND)
        except PermissionDenied as e:
            return Response({"detail": str(e)}, status=status.HTTP_403_FORBIDDEN)


class FriendHangoutView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        friend_id = self.kwargs["friend_id"]
        semester = self.kwargs["semester"]

        if Friend.objects.filter(
            Q(user1=user, user2=friend_id) | Q(user1=friend_id, user2=user)
        ).exists():
            # user and friend_id are friends
            try:
                hangout_intervals = get_hangout_intervals_of_users(
                    semester, [user.id, friend_id]
                )
            except ValueError as e:
                return Response(
                    {"detail": str(e)},
                    status=status.HTTP_404_NOT_FOUND,
                )

            # remove hangout intervals that last lte 10 mins
            hangout_intervals = [
                interval
                for interval in hangout_intervals
                if (
                    (
                        datetime.combine(date.today(), interval[2])
                        - datetime.combine(date.today(), interval[1])
                    ).seconds
                    > 600
                )
            ]

            return Response(
                {
                    "meetings": MeetingIntervalSerializer(
                        hangout_intervals, many=True
                    ).data
                }
            )

        else:
            return Response(
                {"detail": "Access only allowed to friend."},
                status=status.HTTP_403_FORBIDDEN,
            )


            except TimeTable.DoesNotExist:
                return Response(
                    {"detail": "No timetable exists for given user and semester."},
                    status=status.HTTP_404_NOT_FOUND,
                )
        else:
            return Response(
                {"detail": "Access only allowed to friend."},
                status=status.HTTP_403_FORBIDDEN,
            )


class GenerateRequestCodeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        """
        If the user has a valid code, extend the valid time and return the same code.
        If the user doesn't have a valid code, generate a valid code and return the newly generated code.
        """

        (code, expires_at) = (None, None)
        current_code = FriendCode.objects.filter(generated_by=request.user)
        if current_code.exists():
            friend_code = current_code.first()
            # Check the valid time of the code. If the code is valid, extend the valid time.
            if friend_code.expires_at >= timezone.now():
                friend_code.expires_at = timezone.now() + timezone.timedelta(
                    hours=settings.FRIENDS["FRIEND_CODE_EXPIRATION"]
                )
                friend_code.save()
                (code, expires_at) = (friend_code.code, friend_code.expires_at)

            # If the code is not valid, remove any existing code and generate a new code.
            else:
                current_code.delete()

        if code is None:
            rand_code = get_random_code(settings.FRIENDS["FRIEND_CODE_LENGTH"])
            expires_at = timezone.now() + timezone.timedelta(
                hours=settings.FRIENDS["FRIEND_CODE_EXPIRATION"]
            )
            friend_code = FriendCode(
                code=rand_code, expires_at=expires_at, generated_by=request.user
            )
            friend_code.save()
            (code, expires_at) = (friend_code.code, friend_code.expires_at)

        return Response(
            {"code": code, "expires_at": expires_at}, status=status.HTTP_201_CREATED
        )


class RevokeRequestCodeView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        """
        Revoke the user's friend request code if any exist.
        """
        current_code = FriendCode.objects.filter(generated_by=request.user)
        if current_code.exists():
            current_code.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)


class AcceptFriendRequestView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        code = str(request.query_params.get("code"))
        if not code:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        if not is_valid_code(code, settings.FRIENDS["FRIEND_CODE_LENGTH"]):
            return Response(status=status.HTTP_404_NOT_FOUND)

        try:
            friend_code = FriendCode.objects.get(code=code)
        except FriendCode.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if friend_code.expires_at < timezone.now():
            friend_code.delete()
            return Response(status=status.HTTP_404_NOT_FOUND)

        friend = Friend(user1=friend_code.generated_by, user2=request.user)
        friend.save()
        friend_code.delete()
        return Response(
            {
                "detail": "Friend success.",
                "user": {
                    "id": friend_code.generated_by.id,
                    "name": friend_code.generated_by.name,
                },
            },
            status=status.HTTP_201_CREATED,
        )
