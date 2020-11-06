from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("<int:room>", views.room, name="room"),
    path("send", views.send, name="send"),
    path("create_room", views.create_room, name="create_room"),
]
