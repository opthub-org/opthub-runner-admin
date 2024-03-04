"""
scorerで使うhistoryを作成するクラス．

"""
from utils.cache import Cache
from utils.converter import decimal_to_float
from utils.dynamoDB import DynamoDB



class ScorerHistory:
    def __init__(self, match_id, participant_id, cache : Cache, dynamodb : DynamoDB):
        """
        Parameters
        ----------
        match_id : str
            ScorerHistoryを作成するMatchID．
        participant_id : str
            ScorerHistoryを作成するParticipantID．
        dynamodb : DynamoDB
            キャッシュにないデータを取ってくるためのDB．

        """
        self.loaded_cachename = match_id + "#" + participant_id
        self.cache = cache
        self.dynamodb = dynamodb

    
    def load_until_trial_no(self, trial_no):
        """
        trial_no番目までのhistoryのうち，CacheにないデータをDBから取ってきてCacheに格納
        
        """
        self.cache.load(self.loaded_cachename)
        loaded_trial_no = self.cache.get_length_of_values()

        if loaded_trial_no >= trial_no:
            return
        
        evaluation_primary_keys = [{"ID": "Evaluations#" + self.loaded_cachename,
                                       "Trial": f"Trial{no}"} for no in range(loaded_trial_no + 1, trial_no + 1)]
        score_primary_keys = [{"ID": "Scores#" + self.loaded_cachename,
                                       "Trial": f"Trial{no}"} for no in range(loaded_trial_no + 1, trial_no + 1)]
        
        evaluations = self.dynamodb.batch_get_item(evaluation_primary_keys, "TrialNo", "Objective", "Constraint", "Info")
        scores = self.dynamodb.batch_get_item(score_primary_keys, "TrialNo", "Score")

        history_after_loaded_trial_no = {} # trial_no番目よりも後(trial_no ~ self.loaded_trial_no)のhistoryのデータ

        for evaluation in evaluations:
            if evaluation["Status"] == "Success":
                history_after_loaded_trial_no[str(int(evaluation["TrialNo"]))] = {"Objective": decimal_to_float(evaluation["Objective"]),
                                                                                  "Constraint": decimal_to_float(evaluation["Constraint"]),
                                                                                  "Info": decimal_to_float(evaluation["Info"])}
        for score in scores:
            if score["Status"] == "Success":
                history_after_loaded_trial_no[str(int(score["TrialNo"]))]["Score"] = decimal_to_float(score["Score"])

                # キャッシュに追加
                self.cache.append(str(int(score["TrialNo"])), history_after_loaded_trial_no[str(int(score["TrialNo"]))])

        assert trial_no == self.cache.get_length_of_values()
    

    def write(self, trial_no, objective, constraint, info, score):
        self.cache.append(str(trial_no), {"Objective": objective, "Constraint": constraint, "Info": info, "Score": score})

    
    



    

