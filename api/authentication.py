from rest_framework.permissions import SAFE_METHODS, AllowAny, BasePermission


class CustomAllowAny(AllowAny):
    def authenticate(self, *args, **kwargs):
        return True