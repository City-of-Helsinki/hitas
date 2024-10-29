import base64
import json
import uuid
from unittest.mock import MagicMock, patch

import pytest
from social_django.models import UserSocialAuth

from hitas.helauth.pipelines import migrate_user_from_tunnistamo_to_tunnistus
from hitas.helauth.types import IDToken
from hitas.tests.factories import UserFactory
from users.models import User


@pytest.mark.django_db
def test__migrate_user_from_tunnistamo_to_tunnistus__existing_tunnistamo_user():
    old_user = UserFactory.create(email="test.user@mail.test", username="old-test-user")
    new_user = UserFactory.create(email="test.user@mail.test", username="new-test-user")
    old_social_uid = str(uuid.uuid4())
    new_social_uid = str(uuid.uuid4())
    UserSocialAuth.objects.create(user=old_user, provider="tunnistamo", uid=old_social_uid)
    UserSocialAuth.objects.create(user=new_user, provider="tunnistamo", uid=new_social_uid)
    # First login of a not-yet-migrated user
    with patch("hitas.helauth.pipelines.IDToken.from_string", MagicMock()) as id_token_mock:
        id_token_mock.return_value.email = "test.user@mail.test"
        migrate_user_from_tunnistamo_to_tunnistus(None, None, {"id_token": None}, new_user)
    assert User.objects.count() == 1, "There should be only one user after migration."
    assert User.objects.filter(pk=old_user.pk).exists(), "The old user should exist."
    assert User.objects.filter(username="new-test-user").exists(), "The old user should have the new username."
    assert UserSocialAuth.objects.count() == 1, "There should be only one UserSocialAuth after migration."
    assert UserSocialAuth.objects.filter(uid=new_social_uid).exists(), "The new UserSocialAuth should exist."
    # Second login after initial migration
    user_logging_in = User.objects.get(email="test.user@mail.test")
    with patch("hitas.helauth.pipelines.IDToken.from_string", MagicMock()) as id_token_mock:
        id_token_mock.return_value.email = "test.user@mail.test"
        result = migrate_user_from_tunnistamo_to_tunnistus(None, None, {"id_token": None}, user_logging_in)
    assert (
        result["user"] is user_logging_in
    ), "The second login should return the user through the migration unaffected."


@pytest.mark.django_db
def test__migrate_user_from_tunnistamo_to_tunnistus__user_is_none():
    result = migrate_user_from_tunnistamo_to_tunnistus(None, None, {"id_token": None}, None)
    assert result == {"user": None}


@pytest.mark.django_db
def test__migrate_user_from_tunnistamo_to_tunnistus__id_token_is_none():
    user = User()
    result = migrate_user_from_tunnistamo_to_tunnistus(None, None, {"id_token": None}, user)
    assert result["user"] == user


@pytest.mark.django_db
def test__IDToken_from_string():
    payload = {
        "iss": "test",
        "sub": "test",
        "aud": "test",
        "jti": "test",
        "exp": 1,
        "iat": 1,
        "auth_time": 1,
        "amr": "test",
        "loa": "low",
    }
    payload_json = json.dumps(payload)
    jwt_header_part = ""
    jwt_payload_part = base64.urlsafe_b64encode(payload_json.encode("utf-8")).decode("utf-8").rstrip("=")
    jwt_signature_part = ""
    id_token_string = f"{jwt_header_part}.{jwt_payload_part}.{jwt_signature_part}"
    id_token = IDToken.from_string(id_token_string)
    assert id_token.iss == "test", "The IDToken should have the correct issuer."
    assert id_token.is_ad_login is False, "The IDToken should not be an AD login."
    assert id_token.is_profile_login is False, "The IDToken should not be a Helsinki profile login."
    assert id_token.is_strong_login is False, "The IDToken should not be strongly authenticated."
