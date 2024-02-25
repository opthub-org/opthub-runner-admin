import boto3
from utils.converter import decimal_to_number, number_to_decimal
from time import sleep

class DynamoDB:
    def __init__(self):
        self.dynamoDB = boto3.resource("dynamodb", endpoint_url="http://localhost:8000",
                                       region_name="localhost",
                                       aws_access_key_id="aaaaa",
                                       aws_secret_access_key="aaaaa")
        self.table = self.dynamoDB.Table("opthub-dynamodb-participant-trials-dev")
    
    def fetch_item(self, key):
        return decimal_to_number(self.table.get_item(Key=key).get("Item"))
        
    def put_item(self, item):
        item = number_to_decimal(item)
        self.table.put_item(Item=item)

    def fetch_items(self, keys, *attributes):

        batch_keys = {
            "opthub-dynamodb-participant-trials-dev": {
                "Keys": keys,
                "ProjectionExpression": " ,".join([f'#attr{i + 1}' for i in range(len(attributes))]),
                "ExpressionAttributeNames": {f'#attr{i + 1}': attributes[i] for i in range(len(attributes))}
            }
        }

        response = self.dynamoDB.batch_get_item(RequestItems=batch_keys)

        return response["Responses"]["opthub-dynamodb-participant-trials-dev"]
        

    


        
    

