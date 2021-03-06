from rest_framework import serializers
from rest_framework_jwt.settings import api_settings
from django.contrib.auth.models import User
from web_chat.chat.models import Room, Apply

class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('username',)


class UserSerializerWithToken(serializers.ModelSerializer):

    token = serializers.SerializerMethodField()
    password = serializers.CharField(write_only=True)

    def get_token(self, obj):
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

        payload = jwt_payload_handler(obj)
        token = jwt_encode_handler(payload)
        return token

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance

    class Meta:
        model = User
        fields = ('token', 'username', 'password')


class RoomSerializer(serializers.ModelSerializer):
    users = serializers.SerializerMethodField()
    applys = serializers.SerializerMethodField()

    def get_users(self, obj):
        related_users = User.objects.filter(room=obj['id'])
        return [UserSerializer(user).data for user in related_users]

    def get_applys(self, obj):
        related_applys = Apply.objects.filter(room=obj['id'])
        return [ApplySerializer(app).data for app in related_applys]

    class Meta:
        model = Room
        fields =('id', 'name', 'private', 'users', 'applys')
        depth=1

class ApplySerializer(serializers.ModelSerializer):
    user = serializers.SerializerMethodField()

    def get_user(self, obj):
        return UserSerializer(obj.user).data

    class Meta:
        model = Apply
        fields = ('user', 'room', 'status')
