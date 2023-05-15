from typing import TYPE_CHECKING

from django.conf import settings
from rest_framework.permissions import BasePermission

if TYPE_CHECKING:
    from rest_framework.request import Request
    from rest_framework.views import APIView

from users.models import User


class IsAdminOrHasRequiredADGroups(BasePermission):
    def has_permission(self, request: "Request", view: "APIView") -> bool:
        # Workaround to ensure DjangoModelPermissions are not applied
        # to the root view when using DefaultRouter.
        if getattr(view, "_ignore_model_permissions", False):
            return True

        # Non authenticate users are not allowed
        if not request.user:
            return False

        # Admin users are always allowed
        if request.user.is_staff:
            return True

        # Only allow Helsinki profile users from this point
        if not isinstance(request.user, User):
            return False

        # Helsinki profile users require certain AD groups
        user: User = request.user
        if user.ad_groups.filter(name__in=settings.ALLOWED_AD_GROUPS).exists():
            return True
        return False
