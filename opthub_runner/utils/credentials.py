"""This module contains the class related to credentials."""

import shelve
import tempfile
import time
from pathlib import Path

import boto3
import jwt

CLIENT_ID = "24nvfsrgbuvu75h4o8oj2c2oek"


class Credentials:
    """The credentials class. To store and manage the credentials."""

    file_path: Path
    access_token: str
    refresh_token: str
    expire_at: str
    uid: str
    username: str

    def __init__(self) -> None:
        """Initialize the credentials context with a persistent temporary file."""
        temp_dir = tempfile.gettempdir()
        temp_file_name = "opthub_credentials"
        self.file_path = Path(temp_dir) / temp_file_name

    def load(self) -> None:
        """Load the credentials from the shelve file."""
        with shelve.open(str(self.file_path)) as db:
            self.access_token = db.get("access_token", str)
            self.refresh_token = db.get("refresh_token", str)
            self.expire_at = db.get("expire_at", str)
            self.uid = db.get("uid", str)
            self.username = db.get("username", str)
            # refresh the access token if it is expired
            if self.is_expired() and not self.refresh_access_token():
                self.clear_credentials()
                raise Exception("Failed to refresh authentication token. Please re-login.")
            db.close()

    def update(self) -> None:
        """Update the credentials in the shelve file."""
        with shelve.open(str(self.file_path)) as db:
            db["access_token"] = self.access_token
            db["refresh_token"] = self.refresh_token
            # decode the access token to get the expire time, user id and user name
            token = jwt.decode(self.access_token, options={"verify_signature": False})
            db["expire_at"] = token.get("exp")
            db["uid"] = token.get("sub")
            db["username"] = token.get("username")
            db.sync()

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

    def refresh_access_token(self) -> bool:
        """Refresh the access token using refresh token."""
        client = boto3.client("cognito-idp", region_name="ap-northeast-1")
        try:
            response = client.initiate_auth(
                AuthFlow="REFRESH_TOKEN_AUTH",
                AuthParameters={"REFRESH_TOKEN": self.refresh_token},
                ClientId=CLIENT_ID,
            )
            self.access_token = response["AuthenticationResult"]["AccessToken"]
            self.expire_at = jwt.decode(self.access_token, options={"verify_signature": False})["exp"]
            return True
        except Exception as e:
            return False

    def cognito_login(self, username: str, password: str) -> None:
        """Login to cognito user pool. And update the credentials.

        Args:
            username (str): username
            password (str): password
        """
        client = boto3.client("cognito-idp", region_name="ap-northeast-1")

        response = client.initiate_auth(
            AuthFlow="USER_PASSWORD_AUTH",
            AuthParameters={"USERNAME": username, "PASSWORD": password},
            ClientId=CLIENT_ID,
        )
        self.access_token = response["AuthenticationResult"]["AccessToken"]
        self.refresh_token = response["AuthenticationResult"]["RefreshToken"]
        self.update()

    def clear_credentials(self) -> None:
        """Clear the credentials in the shelve file."""
        with shelve.open(str(self.file_path)) as db:
            db["access_token"] = ""
            db["refresh_token"] = ""
            db["expire_at"] = ""
            db["uid"] = ""
            db["username"] = ""
            db.sync()
        self.access_token = ""
        self.refresh_token = ""
        self.expire_at = ""
        self.uid = ""
        self.username = ""
