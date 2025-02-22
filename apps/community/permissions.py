from rest_framework import permissions

    
class IsAuthorOrAdmin(permissions.BasePermission):
    """
    Allows edit/delete only if the user is the author or an admin.
    Used for posts, comments, and replies.
    """
    def has_object_permission(self, request, view, obj):
        # Allow GET requests - this permission doesn't concern GET requests
        if request.method in permissions.SAFE_METHODS:  
            return True
        
        # Allow edit/delete only if the user is the author or an admin
        return request.user and request.user.is_authenticated and (
            obj.author == request.user or request.user.is_staff
        )
    
from .models import Board, Post, Comment

class IsVerifiedAndInstitutionAssociated(permissions.BasePermission):
    """
    Enforces that the user is authenticated and verified (or is admin)
    and, for non-admins, the user's associated institution matches the institution
    of the target object (Board, Post, or Comment).
    """
    def has_permission(self, request, view):
        # Basic authentication and verification check.
        if not (request.user and request.user.is_authenticated and 
                (getattr(request.user, "is_verified", False) or request.user.is_staff)):
            return False
        
        # Admin bypasses institution check.
        if request.user.is_staff:
            return True
    
        if request.method == "POST":
            # When reading a list of Posts or creating a Post, the view should include "board_id"
            if "board_id" in view.kwargs:
                try:
                    board = Board.objects.get(pk=view.kwargs["board_id"])
                except Board.DoesNotExist:
                    return False
                return board.institution == getattr(request.user, "institution", None)
            # When reading comments/creating a comment or reply/reporting a post, the view should include "post_id"
            elif "post_id" in view.kwargs:
                try:
                    post = Post.objects.get(pk=view.kwargs["post_id"])
                except Post.DoesNotExist:
                    return False
                return post.board.institution == getattr(request.user, "institution", None)
            # When creating a reply/reporting a comment, the view should include "comment_id"
            elif "comment_id" in view.kwargs:
                try:
                    comment = Comment.objects.get(pk=view.kwargs["comment_id"])
                except Comment.DoesNotExist:
                    return False
                return comment.post.board.institution == getattr(request.user, "institution", None)
        
        return True

    def has_object_permission(self, request, view, obj):
        # Admin bypasses institution check.
        if request.user.is_staff:
            return True

        user_inst = getattr(request.user, "institution", None)
        # Determine the institution of the object:
        if hasattr(obj, "institution"):
            # Board
            obj_inst = obj.institution
        elif hasattr(obj, "board"):
            # Post
            obj_inst = obj.board.institution
        elif hasattr(obj, "post"):
            # Comment
            obj_inst = obj.post.board.institution
        else:
            return False  # Unknown object type.

        return user_inst == obj_inst