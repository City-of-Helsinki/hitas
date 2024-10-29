from __future__ import annotations

import enum
from dataclasses import dataclass
from typing import Literal, TypedDict

from social_django.models import DjangoStorage, UserSocialAuth
from social_django.strategy import DjangoStrategy

from hitas.helauth.utils import get_jwt_payload


class ADLoginAMR(enum.Enum):
    HELSINKI_ADFS = "helsinki_adfs"
    HELSINKIAD = "helsinkiad"
    HELSINKIAZUREAD = "helsinkiazuread"
    EDUAD = "eduad"


class ProfileLoginAMR(enum.Enum):
    SUOMI_FI = "suomi_fi"
    HELTUNNISTUSSUOMIFI = "heltunnistussuomifi"


@dataclass
class IDToken:
    iss: str
    """token issuer: tunnistamo url"""
    sub: str
    """token subject: uuid"""
    aud: str
    """token audience: tilavaraus-{env}"""
    jti: str
    """JWT ID: uuid"""
    typ: Literal["ID"]
    """token type: ID"""
    exp: int
    """token expiration date: unix epoch timestamp"""
    iat: int
    """token issued-at: unix epoch timestamp"""
    auth_time: int
    """when end-user auth occurred: unix epoch timestamp"""
    nonce: str
    """random string"""
    at_hash: str
    """access token hash: sha256"""
    name: str
    """user name"""
    preferred_username: str
    """user preferred username"""
    given_name: str
    """user given name"""
    family_name: str
    """user family name"""
    email: str
    """user email"""
    email_verified: bool
    """Whether the is email verified or not"""
    ad_groups: list[str]
    """list of ad groups the user belongs to"""
    azp: str
    """authorized party: tilavaraus-{env}"""
    sid: str
    """session id: uuid"""
    session_state: str
    """session state: uuid"""
    amr: str | list[str]
    """
    authentication methods reference:
    suomi_fi | heltunnistussuomifi | helsinki_adfs | helsinkiad | helsinkiazuread | eduad
    """
    loa: Literal["substantial", "low"]
    """level of authentication"""

    @classmethod
    def from_string(cls, token: str) -> IDToken | None:
        try:
            payload = get_jwt_payload(token)
        except Exception:
            return None

        return cls(
            iss=payload["iss"],
            sub=payload["sub"],
            aud=payload["aud"],
            jti=payload["jti"],
            typ=payload.get("typ", ""),  # type: ignore[arg-type]
            exp=payload["exp"],
            iat=payload["iat"],
            auth_time=payload["auth_time"],
            nonce=payload.get("nonce", ""),
            at_hash=payload.get("at_hash", ""),
            name=payload.get("name", ""),
            preferred_username=payload.get("preferred_username", ""),
            given_name=payload.get("given_name", ""),
            family_name=payload.get("family_name", ""),
            email=payload.get("email", ""),
            email_verified=payload.get("email_verified", False),
            ad_groups=payload.get("ad_groups", []),
            azp=payload.get("azp", ""),
            sid=payload.get("sid", ""),
            session_state=payload.get("session_state", ""),
            amr=payload["amr"],
            loa=payload["loa"],
        )

    @property
    def is_ad_login(self) -> bool:
        amr = self.amr
        if amr is None:
            return False

        if isinstance(amr, str):
            amr = [amr]
        return any(method.value in amr for method in ADLoginAMR)

    @property
    def is_profile_login(self) -> bool:
        amr = self.amr
        if amr is None:
            return False

        if isinstance(amr, str):
            amr = [amr]
        return any(method.value in amr for method in ProfileLoginAMR)

    @property
    def is_strong_login(self) -> bool:
        return self.loa == "substantial"


class UserDetails(TypedDict):
    email: str
    first_name: str | None
    last_name: str | None
    fullname: str | None
    username: str | None


class OIDCResponse(TypedDict):
    access_token: str
    email: str
    email_verified: bool
    expires_in: int
    id_token: str
    nickname: str
    refresh_token: str
    sub: str
    token_type: str


class ExtraKwargs(TypedDict):
    details: UserDetails
    is_new: bool
    new_association: bool
    pipeline_index: int
    social: UserSocialAuth
    storage: DjangoStorage
    strategy: DjangoStrategy
    uid: str
    username: str
