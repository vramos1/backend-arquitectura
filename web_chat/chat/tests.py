from django.test import TestCase
from web_chat.chat.models import Room, Chat, Apply
from django.contrib.auth.models import User

# Create your tests here.


class ChatTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            is_superuser=False, password="test", username="test"
        )
        self.room = Room.objects.create(
            name="test room", private=True, creator=self.user
        )
        self.room.users.add(self.user)
        self.room.save()

        self.message = Chat.objects.create(
            username=self.user.username,
            room=self.room,
            message="this is a test message",
        )

        self.apply = Apply.objects.create(user=self.user, room=self.room)

    def test_get_creator(self):
        creator_username = self.room.get_creator()

        self.assertEqual(creator_username, self.user.username)
        self.assertEqual(creator_username, False)

    def test_get_all_messages(self):

        chats = self.room.get_all_messages()

        self.assertEqual(chats[0].message, self.message.message)

    def test_get_user_and_room(self):
        username_string = self.apply.get_user_and_room()

        correct_string = f"{self.user.username} => {self.room.name}"

        self.assertEqual(username_string, correct_string)
