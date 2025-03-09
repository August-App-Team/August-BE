from django.urls import path
from .views import (
    BoardListCreateView,
    BoardDetailView,
    PostListCreateView,
    PostDetailView,
    PostReactionView,
    CommentListCreateView,
    CommentDetailView,
    CommentReplyView,
    ReportPostView,
    ReportCommentView,
)

urlpatterns = [
    # Boards
    path("boards/", BoardListCreateView.as_view(), name="board-list"),
    path("boards/<int:pk>/", BoardDetailView.as_view(), name="board-detail"),
    
    # Posts
    path("boards/<int:board_id>/posts/", PostListCreateView.as_view(), name="post-list"),
    path("posts/<int:pk>/", PostDetailView.as_view(), name="post-detail"),
    path("posts/<int:post_id>/react/", PostReactionView.as_view(), name="post-react"),

    # Comments
    path("posts/<int:post_id>/comments/", CommentListCreateView.as_view(), name="comment-list"),
    path("comments/<int:pk>/", CommentDetailView.as_view(), name="comment-detail"),
    path("comments/<int:comment_id>/replies/", CommentReplyView.as_view(), name="comment-reply"),

    # Reports
    path("posts/<int:post_id>/report/", ReportPostView.as_view(), name="report-post"),
    path("comments/<int:comment_id>/report/", ReportCommentView.as_view(), name="report-comment"),
]