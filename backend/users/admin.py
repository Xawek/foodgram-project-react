from django.contrib.auth import admin
from django.contrib import admin as reg_admin

from .models import User, Follow


@reg_admin.register(User)
class UserAdmin(admin.UserAdmin):
    list_display = (
        'email',
        'id',
        'username',
        'first_name',
        'last_name',
    )
    list_filter = (
        'email',
        'id',
        'username',
    )
    search_fields = (
        'email',
        'id',
        'username',
    )


reg_admin.site.register(Follow)
