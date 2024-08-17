"""This module contains functions to interact with AppSync API."""

from typing import TypedDict

from gql import Client, gql
from gql.transport.aiohttp import AIOHTTPTransport

from opthub_runner_admin.utils.credentials.credentials import Credentials

API_ENDPOINT_URL = "https://tf5tepcpn5bori46x5cyxh3ehe.appsync-api.ap-northeast-1.amazonaws.com/graphql"


class KeyValue(TypedDict):
    """The type of the KeyValue."""

    key: str
    value: str


class NullableKeyValue(TypedDict):
    """The type of the NullableKeyValue."""

    key: str
    value: str | None


class Problem(TypedDict):
    """The type of the Problem."""

    dockerImage: str


class Indicator(TypedDict):
    """The type of the Indicator."""

    dockerImage: str


class Response(TypedDict):
    """The type of the response."""

    id: str
    problem: Problem
    indicator: Indicator
    problemPublicEnvironments: list[KeyValue]
    indicatorPublicEnvironments: list[KeyValue]
    problemPrivateEnvironments: list[NullableKeyValue]
    indicatorPrivateEnvironments: list[NullableKeyValue]


def get_gql_client() -> Client:
    """Get the GraphQL client.

    Returns:
        The GraphQL client.
    """
    credentials = Credentials()
    credentials.load()
    if credentials.access_token is None:
        msg = "Please login first."
        raise Exception(msg)
    headers = {"Authorization": f"Bearer {credentials.access_token}"}
    transport = AIOHTTPTransport(url=API_ENDPOINT_URL, headers=headers)
    return Client(transport=transport, fetch_schema_from_transport=True)


def fetch_match_response_by_match_uuid(match_uuid: str) -> Response:
    """Fetch match by MatchUUID using GraphQL.

    Args:
        match_uuid: The match UUID.


    Returns:
        The match.
    """
    client = get_gql_client()
    variables = {"id": match_uuid}

    query = gql("""query getMatch(
                $id: String) {
                getMatch(
                id: $id) {
                id
                problem {
                dockerImage
                }
                indicator {
                dockerImage
                }
                problemPublicEnvironments {
                  key
                  value
                }
                indicatorPublicEnvironments {
                  key
                  value
                }
                problemPrivateEnvironments {
                  key
                  value
                }
                indicatorPrivateEnvironments {
                  key
                  value
                }}}""")

    response = client.execute(query, variable_values=variables)

    match = response["getMatch"]

    return {
        "id": match["id"],
        "problem": {"dockerImage": match["problem"]["dockerImage"]},
        "indicator": {"dockerImage": match["indicator"]["dockerImage"]},
        "problemPublicEnvironments": [
            {"key": env["key"], "value": env["value"]} for env in match["problemPublicEnvironments"]
        ],
        "indicatorPublicEnvironments": [
            {"key": env["key"], "value": env["value"]} for env in match["indicatorPublicEnvironments"]
        ],
        "problemPrivateEnvironments": [
            {"key": env["key"], "value": env.get("value")} for env in match["problemPrivateEnvironments"]
        ],
        "indicatorPrivateEnvironments": [
            {"key": env["key"], "value": env.get("value")} for env in match["indicatorPrivateEnvironments"]
        ],
    }
