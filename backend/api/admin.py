from django.contrib import admin
from .models import User, UserProfile

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("email", "username", "is_superuser", "is_staff", "date_joined")
    search_fields = ("email", "username")
    list_filter = ("is_superuser", "is_staff", "date_joined")
    ordering = ("email",)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user_email", "user_username", "name", "dob", "created_at")
    search_fields = ("name", "user__email", "user__username",)
    list_filter = ("created_at",)
    ordering = ("-created_at",)

    @admin.display(description="Email")
    def user_email(self, obj):
        return obj.user.email

    @admin.display(description="Username")
    def user_username(self, obj):
        return obj.user.username
