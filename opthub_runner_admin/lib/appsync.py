"""This module contains functions to interact with AppSync API."""

from typing import TypedDict

from gql import Client, gql
from gql.transport.aiohttp import AIOHTTPTransport

from opthub_runner_admin.utils.credentials.credentials import Credentials


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


def get_gql_client(process_name: str, dev: bool) -> Client:
    """Get the GraphQL client.

    Args:
        process_name: The process name
        dev: Whether to use the development environment.

    Returns:
        The GraphQL client.
    """
    credentials = Credentials(process_name, dev)
    credentials.load()
    if credentials.access_token is None:
        msg = "Please login first."
        raise ValueError(msg)
    headers = {"Authorization": f"Bearer {credentials.access_token}"}
    if dev:
        from opthub_runner_admin.environments import API_ENDPOINT_URL_DEV

        api_endpoint_url = API_ENDPOINT_URL_DEV
    else:
        from opthub_runner_admin.environments import API_ENDPOINT_URL_PROD

        api_endpoint_url = API_ENDPOINT_URL_PROD

    transport = AIOHTTPTransport(url=api_endpoint_url, headers=headers)
    return Client(transport=transport, fetch_schema_from_transport=True)


def fetch_match_response_by_match_uuid(process_name: str, match_uuid: str, dev: bool) -> Response:
    """Fetch match by MatchUUID using GraphQL.

    Args:
        process_name: The process name
        match_uuid: The match UUID.
        dev: Whether to use the development environment.


    Returns:
        The match.
    """
    client = get_gql_client(process_name, dev)
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
