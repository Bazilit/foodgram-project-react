from django.contrib import admin

from users.models import User


class UserAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'username', 'email', 'first_name',
        'last_name', 'password', 'role',
    )
    list_editable = (
        'username', 'email', 'first_name',
        'last_name', 'password', 'role',
    )
    list_filter = ('username', 'email', 'first_name', 'last_name', 'role',)
    search_fields = ('username', 'email', 'first_name', 'last_name', 'role',)


admin.site.register(User, UserAdmin)

