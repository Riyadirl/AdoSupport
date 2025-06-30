from django.db import models
from django.contrib.auth.models import (
    BaseUserManager,
    AbstractBaseUser,
    PermissionsMixin,
)
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required


class CustomUserManager(BaseUserManager):
    def create_user(
        self, email, username, password=None, role="adolescent", **extra_fields
    ):
        if not email:
            raise ValueError("Email is required")
        if not username:
            raise ValueError("Username is required")
        if not password:
            raise ValueError("Password is required")

        email = self.normalize_email(email)
        extra_fields.setdefault("role", role)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("role", "adolescent")

        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")

        return self.create_user(email, username, password, **extra_fields)


# ------------------------------------------- USER MODEL ----------------------------------------------------


class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICE = [
        ("adolescent", "Adolescent"),
        ("parent", "Parent"),
    ]

    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICE, default="adolescent")
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True


# ------------------------------------ USER PROFILE -----------------------------------


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    name = models.CharField(max_length=50, null=False, blank=False)
    dob = models.DateField(null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    profile_pic = models.ImageField(upload_to="profile_pic/", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


# previous
# def __str__(self):
# return f"{self.user.username}'s Profile"


# Add this to UserProfile class
def save(self, *args, **kwargs):
    if not self.name:
        self.name = self.user.username
    super().save(*args, **kwargs)


@login_required
def get_username(request):
    return JsonResponse({"username": request.user.username})


# ----------------------------------- Chatbot ---------------------------------------
class ChatHistory(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="chat_history"
    )
    query = models.TextField()
    response = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Chat by {self.user.username} at {self.timestamp}"
