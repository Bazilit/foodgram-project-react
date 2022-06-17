from django.contrib import admin

from users.models import Subscription, User


class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'id')
    list_filter = ('username', 'email')
    search_fields = ('username', 'email')
    empty_value_display = '-пусто-'


class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'author')
    list_filter = ('user', 'author')
    search_fields = ('user', )
    empty_value_display = '-пусто-'


admin.site.register(User, UserAdmin)
admin.site.register(Subscription, SubscriptionAdmin)
