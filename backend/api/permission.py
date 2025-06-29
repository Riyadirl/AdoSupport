from rest_framework.permissions import BasePermission

class IsAdolescent(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == 'adolescent'

class IsParent(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == 'parent'