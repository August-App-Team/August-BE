from rest_framework import serializers
from rest_framework.generics import get_object_or_404
from dj_rest_auth.serializers import UserDetailsSerializer

from apps.community.models import Board, Comment, Post, PostReaction, Report, Tag
from apps.courses.models import Institution
from apps.courses.serializers import DepartmentSerializer
from apps.users.serializers import ImageOrUrlField

class AuthorSerializer(UserDetailsSerializer):
    profile_image = ImageOrUrlField()
    department = DepartmentSerializer()

    class Meta:
        model = UserDetailsSerializer.Meta.model
        fields = ["id", "name", "profile_image", "department"]
        read_only_fields = ["name", "profile_image", "department"]


class BoardSerializer(serializers.ModelSerializer):
    institution = serializers.PrimaryKeyRelatedField(allow_null=True, queryset=Institution.objects.all(), required=False)

    class Meta:
        model = Board
        fields = ["id", "institution", "name", "is_anonymous", "description", "allow_delete_edit"]
    
    def validate(self, data):
        request = self.context.get("request")
        if request and not request.user.is_staff:
            user_institution = getattr(request.user, "institution", None)
            data_institution = data.get("institution")
            if data_institution is not None and data_institution != user_institution:
                raise serializers.ValidationError("You can only create boards for your associated institution.")
            else:
                data["institution"] = user_institution
        return data


class PostSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True)
    reaction_score = serializers.SerializerMethodField()
    tag = serializers.StringRelatedField()
    tag_id = serializers.PrimaryKeyRelatedField(
        write_only=True,
        queryset=Tag.objects.all(),
        source="tag",
        allow_null=True,
    )

    class Meta:
        model = Post
        fields = ["id", "board", "author", "content", "tag", "tag_id", "created_at", "updated_at", "reaction_score", "is_quarantined"]
        read_only_fields = ["board", "author", "tag", "created_at", "updated_at", "reaction_score", "is_quarantined"]

    def get_reaction_score(self, obj):
        return obj.reaction_score
    
    def validate(self, attrs):
        # Ensure that the board exists
        if self.context["view"].kwargs.get("board_id"):
            board_id = self.context["view"].kwargs["board_id"]
            board = get_object_or_404(Board, id=board_id)
            attrs["board"] = board
        return attrs
    
    def create(self, validated_data):
        # Set the author to the user making the request
        validated_data["author"] = self.context["request"].user
        return super().create(validated_data)
    
class CommentSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True)
    
    class Meta:
        model = Comment
        fields = ["id", "post", "parent_comment", "author", "content", "created_at", "is_quarantined"]
        read_only_fields = ["post", "parent_comment", "author", "created_at", "is_quarantined"]

    def validate_parent_comment(self, value):
        """Ensure that a reply is not being made to another reply."""
        if value and value.parent_comment:
            raise serializers.ValidationError("Replies to replies are not allowed.")
        return value
    
    def validate(self, attrs):
        # Ensure that the post exists if adding a comment
        if self.context["view"].kwargs.get("post_id"):
            post_id = self.context["view"].kwargs["post_id"]
            post = get_object_or_404(Post, id=post_id)
            attrs["post"] = post
        # Ensure that the parent comment exists, 
        # and is not a reply to another comment if adding a reply
        elif self.context["view"].kwargs.get("comment_id"):
            comment_id = self.context["view"].kwargs["comment_id"]
            parent_comment = get_object_or_404(Comment, id=comment_id)
            parent_comment = self.validate_parent_comment(parent_comment)
            attrs["parent_comment"] = parent_comment
            attrs["post"] = parent_comment.post

        return attrs
    
    def create(self, validated_data):
        # Set the author to the user making the request
        validated_data["author"] = self.context["request"].user
        return super().create(validated_data)
    
class PostReactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostReaction
        fields = ["id", "user", "post", "is_like"]
        read_only_fields = ["user", "post"]

    def create(self, validated_data):
        """Ensure user cannot like/dislike the same post multiple times."""
        user = self.context["request"].user
        validated_data["user"] = user
        post_id = self.context["view"].kwargs["post_id"]
        # Update or create the reaction for the post
        reaction, created = PostReaction.objects.update_or_create(
            user=user, post_id=post_id, defaults={"is_like": validated_data["is_like"]}
        )
        return reaction


class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = ["id", "user", "post", "comment", "created_at"]
        read_only_fields = ["user", "post", "comment", "created_at"]

    def validate(self, attrs):
        """Ensure that only one of `post` or `comment` is set.
        If `post` is set, ensure that it exists. If `comment` is set, ensure that it exists.
        Finally, ensure that only one report can be made per post or comment by a user.
        """
        post = self.context["view"].kwargs.get("post_id")
        comment = self.context["view"].kwargs.get("comment_id")
        if not post and not comment:
            raise serializers.ValidationError("A report must be associated with either a post or a comment.")
        if post and comment:
            raise serializers.ValidationError("A report cannot be associated with both a post and a comment.")
        
        if post:
            post = get_object_or_404(Post, id=post)
            if Report.objects.filter(user=self.context["request"].user, post=post).exists():
                raise serializers.ValidationError("You have already reported this post.")
            attrs["post"] = post
        if comment:
            comment = get_object_or_404(Comment, id=comment)
            if Report.objects.filter(user=self.context["request"].user, comment=comment).exists():
                raise serializers.ValidationError("You have already reported this comment.")
            attrs["comment"] = comment
        return attrs

    def create(self, validated_data):
        """Assign user automatically."""
        user = self.context["request"].user
        validated_data["user"] = user
        report = super().create(validated_data)
        return report