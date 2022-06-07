from django.contrib import admin
from users.models import User, Follow


class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email',)
    list_filter = ('username', 'email',)
    empty_value_display = 'пусто',


admin.site.register(User, UserAdmin)
admin.site.register(Follow)

