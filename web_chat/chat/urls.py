from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("<int:room>", views.room, name="room"),
    path("send", views.send, name="send"),
    path("create_room", views.create_room, name="create_room"),
    path("current_user/", views.current_user),
    path("users/", views.UserList.as_view()),
    path("view_applys/<int:room_id>", views.view_applys),
    path("accept_apply/<int:apply_id>", views.accept_apply),
    path("reject_apply/<int:apply_id>", views.reject_apply),
    path("my_rooms", views.my_rooms),
    path("apply_to_room/<int:room_id>", views.apply_to_room),
]
