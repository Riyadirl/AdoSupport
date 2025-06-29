from rest_framework.exceptions import NotAuthenticated
from django.db import IntegrityError
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
from .utils import success_response, error_response
from .models import User, UserProfile
from .serializers import UserProfileSerializer


# ======================================= login, register ======================================
class RegisterUserView(APIView):
    def post(self, request):
        email = request.data.get("email")
        username = request.data.get("username")
        password = request.data.get("password")
        role = request.data.get("role")

        if role not in ["adolescent", "parent"]:
            return Response(
                {
                    "error": "Invalid role selected. Choose either 'adolescent' or 'parent'."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if User.objects.filter(email=email).exists():
            return Response(
                {"error": "A user with this email already exists."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if User.objects.filter(username=username).exists():
            return Response(
                {"error": "A user with this username already exists."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = User.objects.create_user(
                email=email, username=username, password=password, role=role
            )
            refresh = RefreshToken.for_user(user)
            return Response(
                success_response(
                    message="Registration successful",
                    data={
                        "id": str(user.id),
                        "name": user.get_username(),
                        "email": user.email,
                        "role": user.role,
                        "refresh": str(refresh),
                        "access": str(refresh.access_token),
                    },
                ),
                status=status.HTTP_200_OK,
            )
        except IntegrityError as e:
            return Response(
                {"error": "Database integrity error: " + str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:
            return Response(
                {"error": "An unexpected error occurred: " + str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class LoginUserView(APIView):
    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        if not email or not password:
            return Response(
                {"error": "Email and password are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = authenticate(request, email=email, password=password)
        if user is None:
            return Response(
                {"error": "Invalid credentials. Please try again."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        try:
            refresh = RefreshToken.for_user(user)
            return Response(
                success_response(
                    message="Login successful",
                    data={
                        "id": str(user.id),
                        "name": user.get_username(),
                        "email": user.email,
                        "role": user.role,
                        "refresh": str(refresh),
                        "access": str(refresh.access_token),
                    },
                ),
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"error": "An unexpected error occurred: " + str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


# ============================================ user profile =========================================
class UserProfileView(APIView):
    serializer_class = UserProfileSerializer
    authentication_class = [JWTAuthentication]
    permission_class = [IsAuthenticated]
    parser_class = [MultiPartParser, FormParser]

    def patch(self, request):
        email = request.data.get("email")
        password = request.data.get("password")
        new_password = request.data.get("new_password")

        if not email or not password:
            return Response(
                {"error": "Email and password are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = authenticate(request, email=email, password=password)
        if user is None:
            return Response(
                {"error": "Invalid credentials. Please try again."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        try:
            profile, created = UserProfile.objects.get_or_create(user=request.user)
            serializer = UserProfileSerializer(profile, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(
                    success_response(
                        message="Profile updated successfully.",
                        data={
                            **serializer.data,
                            "refresh": str(RefreshToken.for_user(user)),
                            "access": str(RefreshToken.for_user(user).access_token),
                        },
                    ),
                    status=status.HTTP_200_OK,
                )
            return Response(
                {"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
            )
        except NotAuthenticated:
            return Response(
                {"error": "Authentication credentials were not provided."},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        except Exception as e:
            return Response(
                {"error": "An unexpected error occurred: " + str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


# ==================================== Change Password =========================================
class ChangePasswordView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        email = request.data.get("email")
        current_password = request.data.get("current_password")
        new_password = request.data.get("new_password")

        if not email or not current_password or not new_password:
            return Response(
                error_response(
                    message="Email, current password, and new password are required.",
                    error_type="ValidationError",
                    status_code=400,
                ),
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = authenticate(request, email=email, password=current_password)
        if user is None:
            return Response(
                error_response(
                    message="Invalid email or current password.",
                    error_type="AuthenticationError",
                    status_code=401,
                ),
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if len(new_password) < 8:
            return Response(
                error_response(
                    message="New password must be at least 8 characters long.",
                    error_type="ValidationError",
                    status_code=400,
                ),
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user.set_password(new_password)
            user.save()
            return Response(
                success_response(message="Password updated successfully.", data=None),
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                error_response(
                    message=f"An unexpected error occurred: {str(e)}",
                    error_type="ServerError",
                    status_code=500,
                ),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class ParentView(APIView):
    serializer_class = UserProfileSerializer
    authentication_class = [JWTAuthentication]
    permission_class = [IsAuthenticated]
    parser_class = [MultiPartParser, FormParser]

    def patch(self, request):
        try:
            if request.user.role != "parent":
                return Response(
                    {"error": "Only parents can access this view."},
                    status=status.HTTP_403_FORBIDDEN,
                )

            profile, created = UserProfile.objects.get_or_create(user=request.user)
            serializer = UserProfileSerializer(profile, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(
                {"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
            )
        except NotAuthenticated:
            return Response(
                {"error": "Authentication credentials were not provided."},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        except Exception as e:
            return Response(
                {"error": "An unexpected error occurred: " + str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def get(self, request):
        try:
            if request.user.role != "parent":
                return Response(
                    {"error": "Only parents can access this view."},
                    status=status.HTTP_403_FORBIDDEN,
                )

            profile, created = UserProfile.objects.get_or_create(user=request.user)
            serializer = UserProfileSerializer(profile)
            return Response(serializer.data)
        except NotAuthenticated:
            return Response(
                {"error": "Authentication credentials were not provided."},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        except Exception as e:
            return Response(
                {"error": "An unexpected error occurred: " + str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class AdolescentView(APIView):
    serializer_class = UserProfileSerializer
    authentication_class = [JWTAuthentication]
    permission_class = [IsAuthenticated]
    parser_class = [MultiPartParser, FormParser]

    def patch(self, request):
        try:
            if request.user.role != "adolescent":
                return Response(
                    {"error": "Only adolescents can access this view."},
                    status=status.HTTP_403_FORBIDDEN,
                )

            profile, created = UserProfile.objects.get_or_create(user=request.user)
            serializer = UserProfileSerializer(profile, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(
                {"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
            )
        except NotAuthenticated:
            return Response(
                {"error": "Authentication credentials were not provided."},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        except Exception as e:
            return Response(
                {"error": "An unexpected error occurred: " + str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def get(self, request):
        try:
            if request.user.role != "adolescent":
                return Response(
                    {"error": "Only adolescents can access this view."},
                    status=status.HTTP_403_FORBIDDEN,
                )

            profile, created = UserProfile.objects.get_or_create(user=request.user)
            serializer = UserProfileSerializer(profile)
            return Response(serializer.data)
        except NotAuthenticated:
            return Response(
                {"error": "Authentication credentials were not provided."},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        except Exception as e:
            return Response(
                {"error": "An unexpected error occurred: " + str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


# ==================================== chatbot =====================================
class Chatbot(APIView):
    authentication_class = [JWTAuthentication]
    permission_class = [IsAuthenticated]

    def post(self, request):
        user_ques = request.data.get("query")
        if not user_ques:
            return Response(
                {"error": "Query is required."}, status=status.HTTP_400_BAD_REQUEST
            )
        try:
            openai.api_key = "______"
            response = openai.Completion.create(
                model="",
                prompt=user_ques,
                max_token=150,
                temperature=0.7,
            )
            chatbot_response = response["choice"][0]["text"].strip()
            return Response({"response": chatbot_response}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": f"An error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
