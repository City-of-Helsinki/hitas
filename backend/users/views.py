import json
from base64 import urlsafe_b64decode

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from social_django.models import UserSocialAuth


@method_decorator(ensure_csrf_cookie, name="dispatch")
class CsrfTokenView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request: Request, *args, **kwargs) -> Response:
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserInfoView(APIView):
    def get(self, request: Request, *args, **kwargs) -> Response:
        try:
            user_info = UserSocialAuth.objects.get(user=request.user)
        except UserSocialAuth.DoesNotExist as error:
            from hitas.exceptions import HitasModelNotFound

            raise HitasModelNotFound(UserSocialAuth) from error

        raw_token = user_info.extra_data["id_token"].split(".")[1]
        padded_token = raw_token + "=" * divmod(len(raw_token), 4)[1]
        token_payload = json.loads(urlsafe_b64decode(padded_token))

        data = {
            "first_name": token_payload.get("given_name", request.user.first_name),
            "last_name": token_payload.get("family_name", request.user.last_name),
            "email": token_payload.get("email", request.user.email),
        }
        return Response(data=data, status=status.HTTP_200_OK)
