from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import (
    RegisterUserView,
    LoginUserView,
    AdolescentView,
    ParentView,
    UserProfileView,
    ChangePasswordView,
)

urlpatterns = [
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("register/", RegisterUserView.as_view(), name="user-registration"),
    path("login/", LoginUserView.as_view(), name="user-login"),
    path("adolescent/", AdolescentView.as_view(), name="adolescent"),
    path("parent/", ParentView.as_view(), name="parent"),
    path("profile/", UserProfileView.as_view(), name="user-profile"),
    path("change-password/", ChangePasswordView.as_view(), name="change-password"),
]


# def home_view(request):
# return JsonResponse({"message": "AdoSupport API is running!"})
