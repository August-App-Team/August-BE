from rest_framework import serializers
from dj_rest_auth.serializers import UserDetailsSerializer

from apps.community.models import Board, Comment, Post, PostReaction, Report, Tag
from apps.courses.models import Institution
from apps.users.serializers import ImageOrUrlField

class AuthorSerializer(UserDetailsSerializer):
    profile_image = ImageOrUrlField()

    class Meta:
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
    tag_id = serializers.PrimaryKeyRelatedField(
        write_only=True,
        queryset=Tag.objects.all(),
        source="tag",
        allow_null=True,
    )

    class Meta:
        model = Post
        fields = ["id", "board", "author", "content", "tag", "created_at", "updated_at", "reaction_score", "is_quarantined"]
        read_only_fields = ["author", "created_at", "updated_at", "reaction_score", "is_quarantined"]

    def get_reaction_score(self, obj):
        return obj.reaction_score()
    
    def create(self, validated_data):
        # Set the author to the user making the request
        validated_data["author"] = self.context["request"].user
        return super().create(validated_data)
    
class CommentSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True)
    
    class Meta:
        model = Comment
        fields = ["id", "post", "parent_comment", "author", "content", "created_at", "is_quarantined"]
        read_only_fields = ["author", "created_at", "is_quarantined"]

    def validate_parent_comment(self, value):
        """Ensure that a reply is not being made to another reply."""
        if value and value.parent_comment:
            raise serializers.ValidationError("Replies to replies are not allowed.")
        return value
    
    def create(self, validated_data):
        # Set the author to the user making the request
        validated_data["author"] = self.context["request"].user
        return super().create(validated_data)

class PostReactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostReaction
        fields = ["id", "user", "post", "is_like"]
        read_only_fields = ["user"]

    def create(self, validated_data):
        """Ensure user cannot like/dislike the same post multiple times."""
        user = self.context["request"].user
        validated_data["user"] = user
        # Update or create the reaction for the post
        reaction, created = PostReaction.objects.update_or_create(
            user=user, post=validated_data["post"], defaults={"is_like": validated_data["is_like"]}
        )
        return reaction


class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = ["id", "user", "post", "comment", "created_at"]
        read_only_fields = ["user", "created_at"]

    def validate(self, data):
        """Ensure that only one of `post` or `comment` is set."""
        post = data.get("post")
        comment = data.get("comment")
        if not post and not comment:
            raise serializers.ValidationError("A report must be associated with either a post or a comment.")
        if post and comment:
            raise serializers.ValidationError("A report cannot be associated with both a post and a comment.")
        return data

    def create(self, validated_data):
        """Assign user automatically."""
        user = self.context["request"].user
        validated_data["user"] = user
        report = super().create(validated_data)
        return report