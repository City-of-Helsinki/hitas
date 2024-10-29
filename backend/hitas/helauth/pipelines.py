from typing import Any, Unpack

from django.core.handlers.wsgi import WSGIRequest
from helusers.tunnistamo_oidc import TunnistamoOIDCAuth
from social_django.models import UserSocialAuth

from hitas.helauth.types import ExtraKwargs, IDToken, OIDCResponse
from users.models import User


def migrate_user_from_tunnistamo_to_tunnistus(
    backend: TunnistamoOIDCAuth,
    request: WSGIRequest,
    response: OIDCResponse,
    user: User | None = None,
    **kwargs: Unpack[ExtraKwargs],
) -> dict[str, Any]:
    if user is None:
        return {"user": user}
    id_token = IDToken.from_string(response["id_token"])
    if (
        id_token is not None
        # Token issued by helsinki-tunnistus
        and id_token.iss.endswith("helsinki-tunnistus")
        and id_token.is_ad_login
        and id_token.email not in ("", None)
    ):
        old_user = User.objects.filter(email=id_token.email).exclude(pk=user.pk).first()
        if old_user is None:
            return {"user": user}
        new_user = user
        # Delete the old UserSocialAuth object to prevent conflicts
        UserSocialAuth.objects.filter(user=old_user).delete()
        # Assign the new UserSocialAuth to the old user
        UserSocialAuth.objects.filter(user=new_user).update(user=old_user)
        # Delete the new User object because we want to keep the old User object and its pk and data
        new_user.delete()
        # Update the old user to match the new user for fields that are used to uniquely identify a user
        old_user.uuid = new_user.uuid
        old_user.username = new_user.username
        old_user.save()
        # Pass the old User object along the authentication pipeline
        user = old_user
    return {"user": user}
