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
from rest_framework import permissions, status, serializers, status
from rest_framework.decorators import api_view, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny
from .serializers import UserSerializer, UserSerializerWithToken, RoomSerializer
from django.conf import settings
from requests.exceptions import HTTPError
from social_django.utils import psa
from rest_framework.authtoken.views import ObtainAuthToken
import json


# Create your views here.


class SocialSerializer(serializers.Serializer):
    """
    Serializer which accepts an OAuth2 access token.
    """

    access_token = serializers.CharField(
        allow_blank=False,
        trim_whitespace=True,
    )


@api_view(http_method_names=["POST"])
@permission_classes([AllowAny])
@psa()
def exchange_token(request, backend):
    """
    Exchange an OAuth2 access token for one for this site.

    This simply defers the entire OAuth2 process to the front end.
    The front end becomes responsible for handling the entirety of the
    OAuth2 process; we just step in at the end and use the access token
    to populate some user identity.
    The URL at which this view lives must include a backend field, like:
        url(API_ROOT + r'social/(?P<backend>[^/]+)/$', exchange_token),
    Using that example, you could call this endpoint using i.e.
        POST API_ROOT + 'social/facebook/'
        POST API_ROOT + 'social/google-oauth2/'
    Note that those endpoint examples are verbatim according to the
    PSA backends which we configured in settings.py. If you wish to enable
    other social authentication backends, they'll get their own endpoints
    automatically according to PSA.
    ## Request format
    Requests must include the following field
    - `access_token`: The OAuth2 access token provided by the provider
    """
    serializer = SocialSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        # set up non-field errors key
        # http://www.django-rest-framework.org/api-guide/exceptions/#exception-handling-in-rest-framework-views
        try:
            nfe = settings.NON_FIELD_ERRORS_KEY
        except AttributeError:
            nfe = "non_field_errors"

        try:
            # this line, plus the psa decorator above, are all that's necessary to
            # get and populate a user object for any properly enabled/configured backend
            # which python-social-auth can handle.
            user = request.backend.do_auth(
                serializer.validated_data["access_token"]
            )

        except HTTPError as e:
            # An HTTPError bubbled up from the request to the social auth provider.
            # This happens, at least in Google's case, every time you send a malformed
            # or incorrect access key.
            return Response(
                {
                    "errors": {
                        "token": "Invalid token",
                        "detail": str(e),
                    }
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if user:
            token, _ = Token.objects.get_or_create(user=user)
            return Response({"token": token.key, "username": user.username})
        else:
            # user is not active; at some point they deleted their account,
            # or were banned by a superuser. They can't just log in with their
            # normal credentials anymore, so they can't log in with social
            # credentials either.
            return Response(
                {"errors": {nfe: "This user account is inactive"}},
                status=status.HTTP_400_BAD_REQUEST,
            )
    else:
        # Unfortunately, PSA swallows any information the backend provider
        # generated as to why specifically the authentication failed;
        # this makes it tough to debug except by examining the server logs.
        return Response(
            {"errors": {nfe: "Authentication Failed"}},
            status=status.HTTP_400_BAD_REQUEST,
        )


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


class CurrentUser(APIView):

    permission_classes = (permissions.AllowAny,)

    def get(self, request, format=None):
        """
        Determine the current user by their token, and return their data
        """
        given_token = request.headers["Authorization"].lstrip("JWT")
        current_user = None
        response = {"username": "No user found with that token"}

        for user in User.objects.all():
            token, _ = Token.objects.get_or_create(user=user)
            if token.key == given_token:
                current_user = user
                break

        response = {"username": current_user.username}
        return Response(response)


class GetTheAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):

        """returns token given a username"""

        user = User.objects.get(username=request.data["username"])
        token, created = Token.objects.get_or_create(user=user)  ##
        return Response(
            {
                "token": token.key,  # small token
                "user_id": user.pk,
                "username": user.username,
            }
        )


class UserList(APIView):
    """
    Create a new user. It's called 'UserList' because normally we'd have a get
    method here too, for retrieving a list of all User objects.
    """

    permission_classes = (permissions.AllowAny,)

    def post(self, request, format=None):
        print("request user list", request.data)
        serializer = UserSerializerWithToken(data=request.data)
        if serializer.is_valid():
            serializer.save()

            for user in User.objects.all():
                token, _ = Token.objects.get_or_create(user=user)
                print("token:", token)

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
