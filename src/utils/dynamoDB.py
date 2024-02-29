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


    def batch_get_item(self, primary_keys, *attributes):
        """
        primary_keyのlistを使ってDynamo DBからitemを複数まとめて取得．

        Parameter
        ---------
        primary_keys : list
            Primary Keyのlist（すなわち，dictのlist）．
        attributes : list
            取得してくる属性．値を渡さなければ，全部取ってくる．

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

        if not attributes:
            batch_keys = {
                self.table_name: {
                    "Keys": primary_keys
                }
            }
            response = self.dynamoDB.batch_get_item(RequestItems=batch_keys)
        else:
            batch_keys = {
                self.table_name: {
                    "Keys": primary_keys,
                    "ProjectionExpression": ",".join([f"#attr{i}" for i in range(len(attributes))]),
                    "ExpressionAttributeNames": {f"#attr{i}": attr for i, attr in enumerate(attributes)}
                }
            }
            response = self.dynamoDB.batch_get_item(RequestItems=batch_keys)

        items = response["Responses"][self.table_name]

        return items
    
    
    def count_items_with_sort_key_prefix(self, partition_key, sort_key_prefix):
        """
        Partition Keyがpartition_keyで，Sort Keyがsort_key_prefixのvalueから始まる項目の数を取ってくる．

        Parameters
        ----------
        partition_key : dict
            Partition Key（keyとvalueのdict）．
        sort_key_prefix : dict
            Sort Keyのkeyとvalueのprefix（接頭辞）のdict．
        
        例
        partition_key = {"ID" : "Evaluations#Match#1#1"}，sort_key_prefix = {"Trial" : "Failed#1"}なら，
        Partition Key（ID）が"Evaluations#Match#1#1"で，Sort Key（Trial）が"Failed#1"から始まる項目の数を取ってくる．
            
        Return
        ------
        count : int
            Partition Keyがpartition_keyで，Sort Keyがsort_key_prefixのvalueから始まる項目の数．

        """
        key_of_partition_key = list(partition_key.keys())[0]
        value_of_partition_key = partition_key[key_of_partition_key]
        key_of_sort_key = list(sort_key_prefix.keys())[0]
        prefix_of_value_of_sort_key = sort_key_prefix[key_of_sort_key]

        response = self.table.query(
            KeyConditionExpression=boto3.dynamodb.conditions.Key(key_of_partition_key).eq(value_of_partition_key) &
            boto3.dynamodb.conditions.Key(key_of_sort_key).begins_with(prefix_of_value_of_sort_key))
        
        count = response["Count"]

        return count

    

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
    items = dynamodb.batch_get_item(primary_keys, "Variable", "UserID", "MatchID")
    print(items)

    print("----- put items -----")
    put_item_4 = {"ID": f"Evaluations#Match#1#Team#1",
                  "Trial": f"Success#1",
                  "TrialNo": 1,
                  "ResourceType": "Evaluation",
                  "MatchID": "Match#1",
                  "CreatedAt": "2024-2-29-15:00:00",
                  "ParticipantID": "Team#1",
                  "StartedAt": "2024-2-29-15:01:00",
                  "FinishedAt": "2024-2-29-15:02:00",
                  "Status": "Success",
                  "Objective": [1, 1],
                  "Constraint": None,
                  "Info": None
    }
    put_item_5 = {"ID": f"Evaluations#Match#1#Team#1",
                  "Trial": f"Failed#1#1",
                  "TrialNo": 1,
                  "ResourceType": "Evaluation",
                  "MatchID": "Match#1",
                  "CreatedAt": "2024-2-29-14:14:00",
                  "ParticipantID": "Team#1",
                  "StartedAt": "2024-2-29-14:15:00",
                  "FinishedAt": "2024-2-29-14:16:00",
                  "Status": "Failed",
                  "ErrorMessage": "Error Message"
    }
    put_item_6 = {"ID": f"Evaluations#Match#1#Team#1",
                  "Trial": f"Failed#1#2",
                  "TrialNo": 1,
                  "ResourceType": "Evaluation",
                  "MatchID": "Match#1",
                  "CreatedAt": "2024-2-29-14:17:00",
                  "ParticipantID": "Team#1",
                  "StartedAt": "2024-2-29-14:18:00",
                  "FinishedAt": "2024-2-29-14:19:00",
                  "Status": "Failed",
                  "ErrorMessage": "Error Message"
    }
    put_item_7 = {"ID": f"Evaluations#Match#1#Team#1",
                  "Trial": f"Failed#2#1",
                  "TrialNo": 2,
                  "ResourceType": "Evaluation",
                  "MatchID": "Match#1",
                  "CreatedAt": "2024-2-29-14:20:00",
                  "ParticipantID": "Team#1",
                  "StartedAt": "2024-2-29-14:21:00",
                  "FinishedAt": "2024-2-29-14:22:00",
                  "Status": "Failed",
                  "ErrorMessage": "Error Message"
    }
    put_item_8 = {"ID": f"Evaluations#Match#1#Team#2",
                  "Trial": f"Failed#1#1",
                  "TrialNo": 1,
                  "ResourceType": "Evaluation",
                  "MatchID": "Match#1",
                  "CreatedAt": "2024-2-29-14:20:00",
                  "ParticipantID": "Team#2",
                  "StartedAt": "2024-2-29-14:21:00",
                  "FinishedAt": "2024-2-29-14:22:00",
                  "Status": "Failed",
                  "ErrorMessage": "Error Message"
    }
    dynamodb.put_item(put_item_4)
    print(put_item_4)
    dynamodb.put_item(put_item_5)
    print(put_item_5)
    dynamodb.put_item(put_item_6)
    print(put_item_6)
    dynamodb.put_item(put_item_7)
    print(put_item_7)
    dynamodb.put_item(put_item_8)
    print(put_item_8)
    print("----- count item of Evaluations#Match#1#Team#1 begin with \"Failed#1\" (Answer is 2)-----")
    count = dynamodb.count_items_with_sort_key_prefix({"ID" : "Evaluations#Match#1#Team#1"}, {"Trial": "Failed#1"})
    print("count :", count)



if __name__ == "__main__":
    main()
        
    

