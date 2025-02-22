from django.db import models
from django.conf import settings
from django.db.models import Q, CheckConstraint, UniqueConstraint

from apps.courses.models import Institution


class Board(models.Model):
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, related_name="boards")
    name = models.CharField(max_length=255, unique=True)
    is_anonymous = models.BooleanField(default=False)
    description = models.TextField()
    allow_delete_edit = models.BooleanField(default=True) # allow posts on this board to be deleted or edited

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    allow_edit = models.BooleanField(default=True)
    allow_delete = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Post(models.Model):
    board = models.ForeignKey("Board", on_delete=models.CASCADE, related_name="posts")
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    content = models.TextField()
    tag = models.ForeignKey("Tag", on_delete=models.SET_NULL, null=True, blank=True, related_name="posts")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_quarantined = models.BooleanField(default=False)

    def can_edit(self):
        return (self.tag is None or self.tag.allow_edit) and self.board.allow_delete_edit

    def can_delete(self):
        return (self.tag is None or self.tag.allow_delete) and self.board.allow_delete_edit
    
    @property
    def reaction_score(self):
        """
        Efficiently calculates net reaction score (likes - dislikes).
        """
        likes = self.reactions.filter(is_like=True).count()
        dislikes = self.reactions.filter(is_like=False).count()
        return likes - dislikes

    def __str__(self):
        return f"Post {self.id} in {self.board.name}"


class PostReaction(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    post = models.ForeignKey("Post", on_delete=models.CASCADE, related_name="reactions")
    is_like = models.BooleanField()  # True for like, False for dislike

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "post"], name="unique_post_reaction")
        ]

    def __str__(self):
        return f"{self.user.name} {'liked' if self.is_like else 'disliked'} Post {self.post.id}"


class Comment(models.Model):
    post = models.ForeignKey("Post", on_delete=models.CASCADE, related_name="comments")
    parent_comment = models.ForeignKey(
        "self", on_delete=models.CASCADE, null=True, blank=True, related_name="replies"
    )
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_quarantined = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.parent_comment and self.parent_comment.parent_comment:
            raise ValueError("Replies to replies are not allowed")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Comment {self.id} on Post {self.post.id}"


class Report(models.Model):
    post = models.ForeignKey("Post", on_delete=models.CASCADE, null=True, blank=True, related_name="reports")
    comment = models.ForeignKey("Comment", on_delete=models.CASCADE, null=True, blank=True, related_name="reports")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            CheckConstraint(
                check=Q(post__isnull=True, comment__isnull=False) | Q(post__isnull=False, comment__isnull=True),
                name="only_one_report_target"
            ),
            UniqueConstraint(fields=["user", "post"], name="unique_post_report", condition=Q(post__isnull=False)),
            UniqueConstraint(fields=["user", "comment"], name="unique_comment_report", condition=Q(comment__isnull=False)),
        ]
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.check_quarantine()

    def check_quarantine(self):
        if self.post:
            report_count = self.post.reports.count()
            if report_count >= 3:
                self.post.is_quarantined = True
                self.post.save()
        elif self.comment:
            report_count = self.comment.reports.count()
            if report_count >= 3:
                self.comment.is_quarantined = True
                self.comment.save()

    def __str__(self):
        return f"Report by {self.user.name} on {'Post' if self.post else 'Comment'} {self.post.id or self.comment.id}"