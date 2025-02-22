from rest_framework import generics
from rest_framework.permissions import AllowAny

from apps.community.models import Board, Comment, Post
from apps.community.pagination import StandardPageNumberPagination
from apps.community.permissions import IsAuthorOrAdmin, IsVerifiedAndInstitutionAssociated
from apps.community.serializers import BoardSerializer, CommentSerializer, PostSerializer, ReportSerializer

# --- Board Views ---
class BoardListCreateView(generics.ListCreateAPIView):
    queryset = Board.objects.all()
    serializer_class = BoardSerializer

    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]  # Board list is public.
        return [IsVerifiedAndInstitutionAssociated()]  # For POST, ensure user’s institution matches (via serializer + permission).


class BoardDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Board.objects.all()
    serializer_class = BoardSerializer
    permission_classes = [IsVerifiedAndInstitutionAssociated]

# --- Post Views ---
class PostListCreateView(generics.ListCreateAPIView):
    serializer_class = PostSerializer
    pagination_class = StandardPageNumberPagination

    def get_queryset(self):
        board_id = self.kwargs["board_id"]
        return Post.objects.filter(board_id=board_id)

    permission_classes = [IsVerifiedAndInstitutionAssociated]


class PostDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer

    def get_permissions(self):
        if self.request.method in ["PUT", "PATCH", "DELETE"]:
            return [IsAuthorOrAdmin()]
        return [IsVerifiedAndInstitutionAssociated()]

# --- Post Reaction ---
class PostReactionView(generics.CreateAPIView):
    serializer_class = PostSerializer
    permission_classes = [IsVerifiedAndInstitutionAssociated]

# --- Comment Views ---
class CommentListCreateView(generics.ListCreateAPIView):
    serializer_class = CommentSerializer

    def get_queryset(self):
        post_id = self.kwargs["post_id"]
        return Comment.objects.filter(post_id=post_id)

    permission_classes = [IsVerifiedAndInstitutionAssociated]


class CommentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    
    def get_permissions(self):
        if self.request.method in ["PUT", "PATCH", "DELETE"]:
            return [IsAuthorOrAdmin()]
        return [IsVerifiedAndInstitutionAssociated()]

# --- Reply ---
class CommentReplyView(generics.CreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [IsVerifiedAndInstitutionAssociated]

# --- Report Views ---
class ReportPostView(generics.CreateAPIView):
    serializer_class = ReportSerializer
    permission_classes = [IsVerifiedAndInstitutionAssociated]


class ReportCommentView(generics.CreateAPIView):
    serializer_class = ReportSerializer
    permission_classes = [IsVerifiedAndInstitutionAssociated]