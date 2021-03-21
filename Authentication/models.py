import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    password = models.CharField(default=None, null=True, max_length=128)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['email'], name='EmailUnique'),
            models.UniqueConstraint(fields=['username'], name='UsernameUnique')
        ]

    def serialize(self):
        return {
            "username": self.username,
        }

