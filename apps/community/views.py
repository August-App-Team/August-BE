from rest_framework import generics, mixins
from rest_framework.permissions import AllowAny

from apps.community.models import Board, Comment, Post, PostReaction, Report
from apps.community.pagination import StandardPageNumberPagination
from apps.community.permissions import IsAuthorOrAdmin, IsVerifiedAndInstitutionAssociated
from apps.community.serializers import BoardSerializer, CommentSerializer, PostReactionSerializer, PostSerializer, ReportSerializer

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
class PostReactionView(mixins.DestroyModelMixin, generics.CreateAPIView):
    queryset = PostReaction.objects.all()
    serializer_class = PostReactionSerializer
    lookup_field = "post_id"
    
    def get_permissions(self):
        if self.request.method == "DELETE":
            return [IsAuthorOrAdmin()]
        return [IsVerifiedAndInstitutionAssociated()]
    
    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)
    
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
class ReportPostView(mixins.DestroyModelMixin, generics.CreateAPIView):
    queryset = Report.objects.all()
    serializer_class = ReportSerializer
    permission_classes = [IsVerifiedAndInstitutionAssociated]
    lookup_field = "post_id"

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)
    
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class ReportCommentView(mixins.DestroyModelMixin, generics.CreateAPIView):
    queryset = Report.objects.all()
    serializer_class = ReportSerializer
    permission_classes = [IsVerifiedAndInstitutionAssociated]
    lookup_field = "comment_id"

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)
    
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)