"""This module contains the class related to credentials."""

import shelve
import time
from pathlib import Path
from typing import Any

import boto3
import jwt
import requests
from jwcrypto import jwk  # type: ignore[import-untyped]

from opthub_runner_admin.models.exception import AuthenticationError, AuthenticationErrorMessage
from opthub_runner_admin.utils.credentials.cipher_suite import CipherSuite
from opthub_runner_admin.utils.credentials.utils import get_opthub_runner_dir

FILE_NAME = "credentials"
CLIENT_ID = "7t7snlnn801j8mjsf97eaart1s"
JWKS_URL = "https://cognito-idp.ap-northeast-1.amazonaws.com/ap-northeast-1_9TAMGx5NT/.well-known/jwks.json"


class Credentials:
    """The credentials class. To store and manage the credentials."""

    file_path: Path
    access_token: str | None
    refresh_token: str | None
    expire_at: str | None
    uid: str | None
    username: str | None

    def __init__(self) -> None:
        """Initialize the credentials context with a persistent temporary file."""
        self.file_path = get_opthub_runner_dir() / FILE_NAME

    def load(self) -> None:
        """Load the credentials from the shelve file."""
        try:
            cipher_suite = CipherSuite()
            with shelve.open(str(self.file_path)) as key_store:  # noqa: S301
                # decrypt the credentials
                self.access_token = cipher_suite.decrypt(key_store.get("access_token", b""))
                self.refresh_token = cipher_suite.decrypt(key_store.get("refresh_token", b""))
                self.expire_at = cipher_suite.decrypt(key_store.get("expire_at", b""))
                self.uid = cipher_suite.decrypt(key_store.get("uid", b""))
                self.username = cipher_suite.decrypt(key_store.get("username", b""))
                key_store.close()
        except Exception as e:
            self.clear_credentials()
            raise AuthenticationError(AuthenticationErrorMessage.LOAD_CREDENTIALS_FAILED) from e
        if self.is_expired():
            self.refresh_access_token()

    def update(self, access_token: str, refresh_token: str) -> None:
        """Update the credentials in the shelve file."""
        cipher_suite = CipherSuite()
        with shelve.open(str(self.file_path)) as key_store:  # noqa: S301
            # encrypt the credentials
            key_store["access_token"] = cipher_suite.encrypt(access_token)
            key_store["refresh_token"] = cipher_suite.encrypt(refresh_token)
            # decode the access token to get the expire time, user id and user name
            public_key = self.get_jwks_public_key(access_token)
            token = self.decode_jwt_token(access_token, public_key)
            key_store["expire_at"] = cipher_suite.encrypt(str(token.get("exp")))
            key_store["uid"] = cipher_suite.encrypt(token.get("sub"))
            key_store["username"] = cipher_suite.encrypt(token.get("username"))
            key_store.sync()
        self.access_token = access_token
        self.refresh_token = refresh_token

    def is_expired(self) -> bool:
        """Determine if the access token has expired.

        Returns:
            bool: True if the token has expired, otherwise False.
        """
        if self.expire_at is None:
            return True
        current_time = int(time.time())
        expire_at_timestamp = int(self.expire_at)
        return current_time > expire_at_timestamp

    def refresh_access_token(self) -> None:
        """Refresh the access token using refresh token.

        Returns:
            bool: true if the access token is refreshed successfully, otherwise false.
        """
        if self.refresh_token is None:
            self.clear_credentials()
            raise AuthenticationError(AuthenticationErrorMessage.REFRESH_FAILED)
        try:
            client = boto3.client("cognito-idp", region_name="ap-northeast-1")
            response = client.initiate_auth(
                AuthFlow="REFRESH_TOKEN_AUTH",
                AuthParameters={"REFRESH_TOKEN": self.refresh_token},
                ClientId=CLIENT_ID,
            )
            access_token = response["AuthenticationResult"]["AccessToken"]
        except Exception as e:
            self.clear_credentials()
            raise AuthenticationError(AuthenticationErrorMessage.REFRESH_FAILED) from e
        self.update(access_token, self.refresh_token)

    def cognito_login(self, username: str, password: str) -> None:
        """Login to cognito user pool. And update the credentials.

        Args:
            username (str): username
            password (str): password
        """
        try:
            client = boto3.client("cognito-idp", region_name="ap-northeast-1")
            response = client.initiate_auth(
                AuthFlow="USER_PASSWORD_AUTH",
                AuthParameters={"USERNAME": username, "PASSWORD": password},
                ClientId=CLIENT_ID,
            )
            access_token = response["AuthenticationResult"]["AccessToken"]
            refresh_token = response["AuthenticationResult"]["RefreshToken"]
        except Exception as e:
            self.clear_credentials()
            raise AuthenticationError(AuthenticationErrorMessage.LOGIN_FAILED) from e
        self.update(access_token, refresh_token)

    def clear_credentials(self) -> None:
        """Clear the credentials in the shelve file."""
        with shelve.open(str(self.file_path)) as key_store:  # noqa: S301
            key_store.clear()
            key_store.sync()
        self.access_token = None
        self.refresh_token = None
        self.expire_at = None
        self.uid = None
        self.username = None

    def get_jwks_public_key(self, access_token: str) -> Any:  # noqa: ANN401
        """Get the public key from the JWKS URL.

        Args:
            access_token (str): access token

        Raises:
            ValueError: fail to get JWKS
            ValueError: fail to get public key

        Returns:
            Any: public key
        """
        try:
            response = requests.get(JWKS_URL, timeout=10)  # set timeout 10 seconds
            response.raise_for_status()
        except requests.RequestException as e:
            raise AuthenticationError(AuthenticationErrorMessage.GET_JWKS_PUBLIC_KEY_FAILED) from e
        jwks = response.json()
        headers = jwt.get_unverified_header(access_token)
        kid = headers["kid"]
        for key in jwks["keys"]:
            if key["kid"] == kid:
                jwk_obj = jwk.JWK(**key)
                public_key_pem = jwk_obj.export_to_pem()
                return public_key_pem
        raise AuthenticationError(AuthenticationErrorMessage.GET_JWKS_PUBLIC_KEY_FAILED)

    def decode_jwt_token(self, access_token: str, public_key: bytes) -> Any:  # noqa: ANN401
        """Decode the JWT token.

        Args:
            access_token (str): access token
            public_key (bytes | Any): public key

        Raises:
            ValueError: fail to get JWKS
            ValueError: fail to get public key

        Returns:
            Any: decoded token
        """
        try:
            return jwt.decode(
                access_token,
                public_key,
                algorithms=["RS256"],
                options={"verify_signature": True},
            )
        except Exception as e:
            raise AuthenticationError(AuthenticationErrorMessage.DECODE_JWT_TOKEN_FAILED) from e
