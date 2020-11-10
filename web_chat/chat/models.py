from django.db import models
from django.contrib.auth.models import User

# from django.contrib.auth.models import AbstractUser

from django.utils import timezone

# Create your models here.


class Room(models.Model):
    name = models.CharField(max_length=60)
    private = models.BooleanField(default=False, null=False)
    users = models.ManyToManyField(User, blank=True)
    creator = models.ForeignKey(
        User, null=True, on_delete=models.SET_NULL, related_name="rooms_created"
    )

    def get_creator(self):
        return self.creator.username

    def get_all_messages(self):
        return self.chat_set.all()


class Apply(models.Model):
    CREATED = "Created"
    REJECTED = "Rejected"
    ACCEPTED = "Accepted"
    POSSIBLE_STATUS = (
        (CREATED, "Created"),
        (REJECTED, "Rejected"),
        (ACCEPTED, "Accepted"),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    status = models.CharField(
        max_length=60, null=False, default=CREATED, choices=POSSIBLE_STATUS
    )

    def get_user_and_room(self):
        return f"{self.user.username} => {self.room.name}"


class Chat(models.Model):
    username = models.CharField(max_length=60, null=False)
    message = models.TextField(default="")
    created_at = models.DateTimeField(auto_now_add=True, null=False)
    room = models.ForeignKey(Room, on_delete=models.SET_NULL, null=True)
    status = models.CharField(
        max_length=60,
        default="normal",
        null=False,
        choices=(
            ("normal", "normal"),
            ("modified", "modified"),
            ("censored", "censored"),
        ),
    )
    modified_message = models.TextField(default="", blank=True)
    censored_message = models.TextField(default="*** Censored Message ***")

    @staticmethod
    def last_50_messages(room_id):
        return (
            Chat.objects.filter(room_id=room_id)
            .order_by("-created_at")
            .all()[:50]
        )

    def __str__(self):
        return f"{self.username}: {self.message} {self.created_at}"


# from chat.core.models.conversation import Conversation


class Session(models.Model):

    username = models.CharField(max_length=255, null=False, blank=False)
    last_read_date = models.DateTimeField(
        auto_now_add=True, blank=False, null=False
    )
    online = models.BooleanField(null=False, blank=False, default=False)

    REQUIRED_FIELDS = []

    def __str__(self):
        return self.username

    def read(self):
        self.last_read_date = timezone.now()
        self.save()

    def unread_messages(self):
        return Chat.objects.filter(created_at__gt=self.last_read_date).count()
