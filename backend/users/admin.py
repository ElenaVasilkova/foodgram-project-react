from django.contrib import admin

from .models import Subscribe, User

EMPTY_STRING: str = '-empty-'

admin.site.site_header = 'Site administration Foodgram'


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'username',
        'first_name',
        'last_name',
        'email'
    )
    search_fields = (
        'email',
        'username',
        'first_name',
        'last_name'
    )
    list_editable = ('email',)
    list_filter = (
        'email',
        'username'
    )
    empty_value_display = EMPTY_STRING


@admin.register(Subscribe)
class SubscribeAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'author',
        'created'
    )
    search_fields = (
        'user__email',
        'author__email'
    )
    list_filter = ('user', 'author')
    empty_value_display = EMPTY_STRING
