from django.contrib import admin
from .models import User, Subscribe


class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'first_name']
    list_filter = ['username', 'email']

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'author')


admin.site.register(User, UserAdmin)
admin.site.register(Subscribe, SubscriptionAdmin)
