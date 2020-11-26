from rest_framework.permissions import BasePermission

from accounts.models import User


class HasRoleAdmin(BasePermission):
    def has_permission(self, request, view):
        user = User.get_user_by_token(request)
        if user is None:
            return False
        return user.role == User.ROLE_ADMIN


class HasRoleAgent(BasePermission):
    def has_permission(self, request, view):
        user = User.get_user_by_token(request)
        if user is None:
            return False
        return user.role == User.ROLE_AGENT


class HasRoleCustomer(BasePermission):
    def has_permission(self, request, view):
        user = User.get_user_by_token(request)
        if user is None:
            return False
        return user.role == User.ROLE_CUSTOMER
