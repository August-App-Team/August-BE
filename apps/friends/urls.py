from django.urls import path
from apps.friends import views

urlpatterns = [
    path("", views.FriendListView.as_view(), name="friends-list"),
    path("<int:friend_id>/", views.FriendDeleteView.as_view(), name="friend-detail"),
    path(
        "<int:friend_id>/tables/semesters/",
        views.FriendTimeTableSemesterList.as_view(),
        name="friend-timetable-semesters",
    ),
    path(
        "<int:friend_id>/tables/<int:semester>/",
        views.FriendTimeTableView.as_view(),
        name="friend-timetable",
    ),
    path(
        "<int:friend_id>/tables/<int:semester>/hangout/",
        views.FriendHangoutView.as_view(),
        name="friend-hangout",
    ),
    path(
        "new-request-code/",
        views.GenerateRequestCodeView.as_view(),
        name="generate-request-code",
    ),
    path(
        "revoke-code/",
        views.RevokeRequestCodeView.as_view(),
        name="revoke-request-code",
    ),
    path(
        "accept/", views.AcceptFriendRequestView.as_view(), name="accept-friend-request"
    ),
]
