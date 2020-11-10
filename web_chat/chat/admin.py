from django.contrib import admin
from web_chat.chat.models import Chat, Room, Apply
from django_admin_listfilter_dropdown.filters import (
    DropdownFilter,
    RelatedDropdownFilter,
    ChoiceDropdownFilter,
)

# Register your models here.
class AdminRoom(admin.ModelAdmin):
    filter_horizontal = ("users",)


admin.site.register(Chat)
admin.site.register(Room, AdminRoom)


@admin.register(Apply)
class ApplyAdmin(admin.ModelAdmin):
    actions = ["reject", "accept"]
    list_display = ["user", "room", "status"]
    list_filter = (
        ("status", ChoiceDropdownFilter),
        ("user", RelatedDropdownFilter),
        ("room", RelatedDropdownFilter),
    )

    def reject(self, request, queryset):
        for apply in queryset:
            if apply.status == apply.CREATED:
                apply.status = apply.REJECTED
                apply.save()

    def accept(self, request, queryset):
        for apply in queryset:
            apply.status = apply.ACCEPTED
            apply.room.users.add(apply.user)
            apply.save()
