from gql import Client, gql
from gql.transport.aiohttp import AIOHTTPTransport
from keys import API_ENDPOINT_URL, API_KEY


def get_gql_client() -> Client:
    """Get the GraphQL client.

    Returns:
        Client: The GraphQL client
    """
    url = API_ENDPOINT_URL
    api_key = API_KEY
    headers = {"x-api-key": api_key}
    transport = AIOHTTPTransport(url=url, headers=headers)
    return Client(transport=transport, fetch_schema_from_transport=True)


def fetch_match_problem_by_match_id(match_id: str, alias: str, client: Client):
    """Fetch problemID and problemEnvironments by MatchID using GraphQL.

    Parameters
    ----------
    match_id: str
      MatchID.
    alias: str
      Match alias.
    client: Client
      GraphQL client.

    Return
    ------
    response: dict
      Dict containing problemID, problemPublicEnvironment, problemSecretEnvironment.

    """
    variables = {"id": match_id, "alias": alias}

    query = gql("""query getMatch(
                $id: String,
                $alias: String) {
                getMatch(
                id: $id,
                alias: $alias) {
                problemID
                problemPublicEnvironment,
                problemSecretEnvironment,
                }
                }""")

    response = client.execute(query, variable_values=variables)

    return response


def fetch_match_indicator_by_match_id(match_id: str, alias: str, client: Client):
    """Fetch indicatorID and indicatorEnvironments by MatchID using GraphQL.

    Parameters
    ----------
    match_id: str
      MatchID.
    alias: str
      Match alias.
    client: Client
      GraphQL client.

    Return
    ------
    response: dict
      Dict containing indicatorID, indicatorPublicEnvironment, indicatorSecretEnvironment.

    """
    variables = {"id": match_id, "alias": alias}

    query = gql("""query getMatch(
                $id: String,
                $alias: String) {
                getMatch(
                id: $id,
                alias: $alias) {
                indicatorID
                indicatorPublicEnvironment,
                indicatorSecretEnvironment,
                }
                }""")

    response = client.execute(query, variable_values=variables)

    return response


def fetch_docker_image_by_problem_id(problem_id: str, alias: str, client: Client):
    """Fetch problemDockerImage by ProblemID using GraphQL.

    Parameters
    ----------
    problem_id: str
      ProblemID.
    alias: str
      Problem alias.
    client: Client
      GraphQL client.

    Return
    ------
    response: dict
      Dict containing problemDockerImage.

    """
    variables = {"id": problem_id, "alias": alias}

    query = gql("""query getProblem(
                $id: String,
                $alias: String) {
                getProblem(
                id: $id,
                alias: $alias) {
                dockerImage
                }
                }""")
    response = client.execute(query, variable_values=variables)

    return response


def fetch_docker_image_by_indicator_id(indicator_id: str, alias: str, client: Client):
    """Fetch indicatorDockerImage by indicatorID using GraphQL.

    Parameters
    ----------
    indicator_id: str
      indicatorID.
    alias: str
      Indicator alias.
    client: Client
      GraphQL client.

    Return
    ------
    response: dict
      Dict containing indicatorDockerImage.

    """
    variables = {"id": indicator_id, "alias": alias}

    query = gql("""
                query getIndicator(
                $id: String,
                $alias: String) {
                getIndicator(
                id: $id,
                alias: $alias) {
                  dockerImage
                }
                }""")
    response = client.execute(query, variable_values=variables)

    return response


def main():
    client = get_gql_client()
    result = fetch_docker_image_by_indicator_id("dd69dc7f-5d82-4f2c-9be7-420a6f77202b", "sphere", client)
    print(result)


if __name__ == "__main__":
    main()
