from django.db import models
from django.contrib.auth import get_user_model
class Friend(models.Model):
    user1 = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='friend1')
    user2 = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='friend2')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user1', 'user2'], name='unique friendship')
        ]

class FriendCode(models.Model):
    code = models.CharField(max_length=8, primary_key=True)
    expires_at = models.DateTimeField()
    generated_by = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)