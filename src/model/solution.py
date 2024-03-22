"""
Solutionの取得

"""
from utils.dynamodb import DynamoDB
from utils.converter import decimal_to_float



def fetch_solution_by_primary_key(match_id, participant_id, trial, dynamodb : DynamoDB):
    """
    Primary Keyを使ってDynamo DBからSolutionを取ってくる関数．

    Parameters
    ----------
    match_id : str
        Matchのid．
    participant_id : str
        UserIDまたはTeamID．
    trial : str
        Trial．
    dynamodb : DynamoDB
        dynamo DBと通信するためのラッパークラスのオブジェクト．
    
    Return
    ------
    solution : dict
        取ってきたSolution．
    """
    primary_key = {"ID" : f"Solutions#{match_id}#{participant_id}",
                   "Trial" : trial}
    
    solution = dynamodb.get_item(primary_key)

    # "Variable"がdecimalのままだと，Solutionの評価で扱いにくくなるため，変換
    solution["Variable"] = decimal_to_float(solution["Variable"])

    return solution


def main():
    dynamodb = DynamoDB("localhost",
                        "aaaaa", "aaaaa", "opthub-dynamodb-participant-trials-dev")
    solution = fetch_solution_by_primary_key("Match#1", "Team#1", "1", dynamodb)
    print("----- solution -----")
    print(solution)


if __name__ == "__main__":
    main()




