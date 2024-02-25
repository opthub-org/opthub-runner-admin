class EvaluationModel:

    def __init__(self, context):
        objective = None
        constraint = None
        
    @staticmethod
    def create_succeeded_data(self, objective, constraint, started_at, finished_at, context):
        # evaluationのデータを作る
        evaluation = {"ID": f'Evaluations#{context["MatchID"]}#{context["UserID"]}',
                     "Trial": f'Success#{self.__solution["Trial"]}',
                     "TrialNo": self.__solution["TrialNo"],
                     "ResourceType": "Evaluation",
                     "CompetitionID": self.__solution["CompetitionID"],
                     "ProblemID": self.__solution["ProblemID"],
                     "IndicatorID": self.__solution["IndicatorID"],
                     "ProblemEnvironments": self.__solution["ProblemEnvironments"],
                     "MethodID": self.__solution["MethodID"],
                     "MatchGroupID": self.__solution["MatchGroupID"],
                     "MatchID": self.__solution["MatchID"],
                     "CreatedAt": self.__solution["CreatedAt"],
                     "UserID": self.__solution["UserID"],
                     "StartedAt": started_at,
                     "FinishedAt": finished_at,
                     "Status": "Success",
                     "FailedNum": 0,
                     "Objective": objective,
                     "Constraint": constraint,
                     "Info": []}
        return evaluation, context
    
    def create_failed_data(self, exc, started_at, finished_at, context):
        return evaluation, context
    
    def fetch_past_evaluations(self, match_id, user_id):
        # 過去の評価を取ってくる
        pass
        
    def fetch_current_evaluation():
        # 現在の評価を取ってくる
        return context
