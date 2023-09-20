from django.contrib import admin
from .models import User, Subscribe
from django.contrib.auth.hashers import make_password


class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'first_name']
    list_filter = ['username', 'email']

    def save_model(self, request, obj, form, change):
        if not obj.pk and obj.password:
            obj.password = make_password(obj.password)
        super().save_model(request, obj, form, change)


class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'author')


admin.site.register(User, UserAdmin)
admin.site.register(Subscribe, SubscriptionAdmin)
