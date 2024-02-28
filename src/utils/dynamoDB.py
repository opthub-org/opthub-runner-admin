"""
Dynamo DBのラッパー．

"""
import boto3


class DynamoDB:
    """
    Dynamo DBのラッパークラス．

    """

    def __init__(self, endpoint_url, region_name, aws_access_key_id,
                 aws_secret_access_key, table_name):
        """
        Parameters
        ----------
        endpoint_url : str
            DynamoDBへの接続先URL．
        region_name : str
            サービスがデプロイされるリージョン．
        aws_access_key_id : str
            AWSアカウントのアクセスキーID．
        aws_secret_access_key : str
            AWSアクセスキーIDに対応する秘密アクセスキー．
        table_name : str
            テーブル名．
        
        """
        self.dynamoDB = boto3.resource("dynamodb", endpoint_url=endpoint_url,
                                       region_name=region_name,
                                       aws_access_key_id=aws_access_key_id,
                                       aws_secret_access_key=aws_secret_access_key)
        self.table_name = table_name
        self.table = self.dynamoDB.Table(self.table_name)
    

    def get_item(self, primary_key):
        """
        primary_keyを使ってDynamo DBからitemを取得．

        Parameter
        ---------
        primary_key : dict
            Primary Key．
        
        Return
        ------
        item : dict
            取得したitem．

        """
        item = self.table.get_item(Key=primary_key).get("Item")
        return item
    
        
    def put_item(self, item):
        """
        Dynamo DBにitemを保存．

        Parameter
        ---------
        item : dict
            Dynamo DBに保存するitem．
        
        """
        self.table.put_item(Item=item)


    def batch_get_item(self, primary_keys):
        """
        primary_keyのlistを使ってDynamo DBからitemを複数まとめて取得．

        Parameter
        ---------
        primary_keys : list
            Primary Keyのlist（すなわち，dictのlist）．

        Return
        ------
        items : list
            取得したitemのlist（すなわち，dictのlist）．
        
        """

        batch_keys = {
            self.table_name: {
                "Keys": primary_keys
            }
        }

        response = self.dynamoDB.batch_get_item(RequestItems=batch_keys)
        items = response["Responses"][self.table_name]

        return items
        

    

def main():

    dynamodb = DynamoDB("http://localhost:8000", "localhost",
                        "aaaaa", "aaaaa", "opthub-dynamodb-participant-trials-dev")
    
    put_item = {"ID": "Solutions#Match#1#Team#3",
                "Trial": "1",
                "ParticipantID": "Team#3",
                "Variable": 2,
                "UserID": "User#1",
                "MatchID": "Match#1", 
                "CreatedAt": "2024-01-05-00:00:00",
                "ResourceType": "Solutions",
                "ID": "Solutions#Match#1#Team#3",
                "TrialNo": 1}
    
    print("----- put item -----")
    dynamodb.put_item(put_item)
    print(put_item)

    primary_key = {"ID": "Solutions#Match#1#Team#3",
                   "Trial": "1"}
    print("----- get item -----")
    got_item = dynamodb.get_item(primary_key)
    print(got_item)


    put_item_1 = {"ID": "Solutions#Match#2#Team#3",
                  "Trial": "1",
                  "ParticipantID": "Team#3",
                  "Variable": [1, 2],
                  "UserID": "User#1",
                  "MatchID": "Match#2", 
                  "CreatedAt": "2024-02-01-00:00:00",
                  "ResourceType": "Solutions",
                  "ID": "Solutions#Match#2#Team#3",
                  "TrialNo": 1}
    put_item_2 = {"ID": "Solutions#Match#3#Team#3",
                  "Trial": "1",
                  "ParticipantID": "Team#3",
                  "Variable": [3, 4],
                  "UserID": "User#1",
                  "MatchID": "Match#3", 
                  "CreatedAt": "2024-03-01-00:00:00",
                  "ResourceType": "Solutions",
                  "ID": "Solutions#Match#3#Team#3",
                  "TrialNo": 1}
    put_item_3 = {"ID": "Solutions#Match#4#Team#3",
                  "Trial": "1",
                  "ParticipantID": "Team#3",
                  "Variable": [5, 6],
                  "UserID": "User#1",
                  "MatchID": "Match#4", 
                  "CreatedAt": "2024-04-01-00:00:00",
                  "ResourceType": "Solutions",
                  "ID": "Solutions#Match#4#Team#3",
                  "TrialNo": 1}
    
    print("----- put items -----")
    dynamodb.put_item(put_item_1)
    print(put_item_1)
    dynamodb.put_item(put_item_2)
    print(put_item_2)
    dynamodb.put_item(put_item_3)
    print(put_item_3)

    print("----- get items -----")
    primary_keys = [{"ID": "Solutions#Match#2#Team#3", "Trial": "1"},
                    {"ID": "Solutions#Match#3#Team#3", "Trial": "1"},
                    {"ID": "Solutions#Match#4#Team#3", "Trial": "1"}]
    items = dynamodb.batch_get_item(primary_keys)
    print(items)



if __name__ == "__main__":
    main()
        
    

