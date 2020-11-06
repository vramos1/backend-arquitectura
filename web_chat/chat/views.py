from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.core import serializers
from django.forms.models import model_to_dict
from django.views.decorators.http import (
    require_GET,
    require_POST,
    require_http_methods,
)
from web_chat.chat.models import Chat, Room
import json

# Create your views here.


@require_GET
def index(request):
    rooms = Room.objects.all()
    if (
        "HTTP_ACCEPT" in request.META
        and request.META["HTTP_ACCEPT"] == "application/json"
    ):
        data = {"rooms": list(rooms.values())}
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


@require_GET
def room(request, room):
    room = get_object_or_404(Room, pk=room)
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
    new_room = Room(name=name)
    new_room.save()
    rooms = Room.objects.all()
    data = {"rooms": list(rooms.values())}
    return JsonResponse(data)
