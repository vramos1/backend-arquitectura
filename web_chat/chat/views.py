from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse, HttpResponseForbidden
from django.core import serializers
from django.forms.models import model_to_dict
from django.views.decorators.http import (
    require_GET,
    require_POST,
    require_http_methods,
)
from web_chat.chat.models import Chat, Room, Apply
from django.contrib.auth.models import User
from rest_framework import permissions, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import UserSerializer, UserSerializerWithToken, RoomSerializer
import json

# Create your views here.


@require_GET
def index(request):
    rooms = Room.objects.all()
    if (
        "HTTP_ACCEPT" in request.META
        and request.META["HTTP_ACCEPT"] == "application/json"
    ):
        serialized_rooms = [
            RoomSerializer(room).data for room in list(rooms.values())
        ]
        data = {"rooms": serialized_rooms}
        return JsonResponse(data)
    return render(request, "index.html", {"rooms": rooms})


@require_POST
def send(request):
    body = json.loads((request.body).decode("utf-8"))
    username = body.get("username")
    message = body.get("message")
    room_id = body.get("room_id")
    new_message = Chat(username=username, message=message, room_id=room_id)
    new_message.save()
    return JsonResponse(
        {
            "id": new_message.id,
            "message": new_message.message,
            "room_id": room_id,
        }
    )


@api_view(["GET"])
def room(request, room):
    room = get_object_or_404(Room, pk=room)
    if room.private and request.user not in room.users.all():
        return HttpResponseForbidden()
    chats = Chat.objects.filter(room=room).order_by("created_at")
    rooms = Room.objects.all()
    if (
        "HTTP_ACCEPT" in request.META
        and request.META["HTTP_ACCEPT"] == "application/json"
    ):
        rooms = list(rooms.values())
        chats = list(chats.values())
        room = model_to_dict(room)
        return JsonResponse({"chats": chats, "room": room, "rooms": rooms})
    return render(
        request, "room.html", {"chats": chats, "room": room, "rooms": rooms}
    )


@require_POST
def create_room(request):
    body = json.loads((request.body).decode("utf-8"))
    name = body.get("name")
    username = body.get("creator")
    private = body.get("private")
    user = User.objects.get(username=username)
    new_room = Room(name=name, creator=user, private=private)
    new_room.save()
    new_room.users.add(user)
    rooms = Room.objects.all()
    serialized_rooms = [
        RoomSerializer(room).data for room in list(rooms.values())
    ]
    data = {"rooms": serialized_rooms}
    return JsonResponse(data)


@api_view(["GET"])
def my_rooms(request):
    rooms = request.user.rooms_created.filter(private=True)
    return JsonResponse({"rooms": list(rooms.values())})


@api_view(["GET"])
def view_applys(request, room_id):
    room = get_object_or_404(Room, pk=room_id)
    user = request.user
    if user.id != room.creator_id and not user.is_superuser:
        return HttpResponseForbidden()

    applys = (
        Apply.objects.select_related("user")
        .select_related("room")
        .filter(room_id=room_id, status=Apply.CREATED)
    )

    applys_returned = []
    for app in applys:
        new_apply = {
            "user": app.user.username,
            "room": app.room.name,
            "id": app.id,
        }
        applys_returned.append(new_apply)
    data = {"applys": applys_returned}
    return JsonResponse(data)


@require_POST
def accept_apply(request, apply_id):
    apply = get_object_or_404(Apply, pk=apply_id)

    if apply.status != apply.CREATED:
        return HttpResponseForbidden()

    apply.status = apply.ACCEPTED
    apply.save()

    apply.room.users.add(apply.user)

    return JsonResponse({})


@require_POST
def reject_apply(request, apply_id):
    apply = get_object_or_404(Apply, pk=apply_id)

    if apply.status != apply.CREATED:
        return HttpResponseForbidden()

    apply.status = apply.REJECTED
    apply.save()

    return JsonResponse({})


@api_view(["POST"])
def apply_to_room(request, room_id):
    new_apply = Apply(user=request.user, room_id=room_id)
    new_apply.save()
    return JsonResponse({})


# JWT AUTHENTICATION VIEWS


@api_view(["GET"])
def current_user(request):
    """
    Determine the current user by their token, and return their data
    """

    serializer = UserSerializer(request.user)
    return Response(serializer.data)


class UserList(APIView):
    """
    Create a new user. It's called 'UserList' because normally we'd have a get
    method here too, for retrieving a list of all User objects.
    """

    permission_classes = (permissions.AllowAny,)

    def post(self, request, format=None):
        serializer = UserSerializerWithToken(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
