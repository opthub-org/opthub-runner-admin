"""
Dynamo DBのラッパー．

"""
import boto3
from boto3.dynamodb.conditions import Key


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


    def get_item_between_least_and_greatest(self, partition_key, partition_key_value, sort_key, least, greatest, *attributes):
        """
        partition_keyがpartition_key_value，sort_keyがleastからgreatestのitemをDynamo DBから複数まとめて取得．

        Parameters
        ----------
        partition_key: str
            Partition Key．
        partition_key_value: str
            Partition Keyの値．
        sort_key: str
            Sort Key．
        least: str
            Sort Keyの下端．
        greatest: str
            Sort Keyの上端．
        attributes : list
            取得してくる属性．値を渡さなければ，全部取ってくる．

        Return
        ------
        items : list
            取得したitemのlist（すなわち，dictのlist）．
        
        """
        if not attributes:
            response = self.table.query(
                KeyConditionExpression=Key(partition_key).eq(partition_key_value) & Key(sort_key).between(least, greatest),
            )
        else:
            response = self.table.query(
                KeyConditionExpression=Key(partition_key).eq(partition_key_value) & Key(sort_key).between(least, greatest),
                ProjectionExpression=",".join([f"#attr{i}" for i in range(len(attributes))]),
                ExpressionAttributeNames={f"#attr{i}": attr for i, attr in enumerate(attributes)}
            )
        items = response["Items"]

        return items


def main():

    dynamodb = DynamoDB("http://localhost:8000", "localhost",
                        "aaaaa", "aaaaa", "opthub-dynamodb-participant-trials-dev")
    
    for i in range(1, 11):
        put_item = {"ID": "Solutions#Match#10#Team#10",
                    "Trial": str(i).zfill(2),
                    "ParticipantID": "Team#10",
                    "Variable": [1, 2],
                    "UserID": "User#1",
                    "MatchID": "Match#10", 
                    "CreatedAt": f"2024-01-05-00:{str(i).zfill(2)}:00",
                    "ResourceType": "Solutions",
                    "ID": "Solutions#Match#10#Team#10",
                    "TrialNo": str(i).zfill(2)}
         
        print("----- put item -----")
        dynamodb.put_item(put_item)
        print(put_item)

    primary_key = {"ID": "Solutions#Match#10#Team#10",
                   "Trial": "03"}
    print("----- get item -----")
    got_item = dynamodb.get_item(primary_key)
    print(got_item)

    print("----- get items -----")
    items = dynamodb.get_item_between_least_and_greatest("ID", "Solutions#Match#10#Team#10", "Trial", "02", "08", "TrialNo", "Variable", "UserID", "MatchID")
    print(items)

if __name__ == "__main__":
    main()