"""
GraphQL経由でMatchの情報を取得

"""



def fetch_match_problem_by_id(match_id):
    """
    GraphQL経由でMatchを取得し，Evaluationに必要なProblemの情報を取得する関数．

    Parameters
    ----------
    match_id : str
        取得するMatchのid．
    
    Returns
    -------
    problem_data : dict
        Problemの情報（ProblemDockerImageとProblemEnvironments）を格納したdict．

    """

    # match_idを使ってGraphQL経由でmatchを取得（未実装なのでとりあえずmock）
    match = {"MatchProblemID" : "Problem#1",
             "MatchProblemPublicEnvironments" : {},
             "MatchProblemPrivateEnvironments" : {}}
    
    problem_id = match["MatchProblemID"]

    # problem_idを使ってGraphQL経由でproblemを取得（未実装なのでとりあえずmock）
    problem = {"ProblemDockerImage" : "(url)"}

    problem_data = {"ProblemDockerImage" : problem["ProblemDockerImage"],
                    "ProblemEnvironments" : dict(**match["MatchProblemPublicEnvironments"], **match["MatchProblemPrivateEnvironments"])}

    return problem_data


def fetch_match_indicator_by_id(match_id):
    """
    GraphQL経由でMatchを取得し，Scoreに必要なIndicatorの情報を取得する関数．

    Parameters
    ----------
    match_id : str
        取得するMatchのid．
    
    Returns
    -------
    indicator_data : dict
        Indicatorの情報（IndicatorDockerImageとIndicatorEnvironments）を格納したdict．

    """

    # match_idを使ってGraphQL経由でmatchを取得（未実装なのでとりあえずmock）
    match = {"MatchIndicatorID" : "Indicator#1",
             "MatchIndicatorPublicEnvironments" : {},
             "MatchIndicatorPrivateEnvironments" : {}}
    
    indicator_id = match["MatchIndicatorID"]

    # indicator_idを使ってGraphQL経由でindicatorを取得（未実装なのでとりあえずmock）
    indicator = {"IndicatorDockerImage" : "(url)"}

    indicator_data= {"IndicatorDockerImage" : indicator["IndicatorDockerImage"],
                     "IndicatorEnvironments" : dict(**match["MatchIndicatorPublicEnvironments"], **match["MatchIndicatorPrivateEnvironments"])}

    return indicator_data