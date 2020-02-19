import boto3
import datetime
import json
import time

dynamodb_resource = boto3.resource('dynamodb')
table = dynamodb_resource.Table('RackOne_DB')
UserID = '30621276'

response = table.get_item(
    Key={
        'UserID': UserID
    }
)


def deleteItem():
    table.delete_item(
        Key={
            'UserID': UserID
        }
    )


item = response['Item']
endTime = datetime.datetime.strptime(item['ExpirationTime'], '%m/%d/%Y %H:%M:%S')
while (True):
    if (datetime.datetime.now() > endTime):
        print("Now")
        # deleteItem()
        break
    else:
        print("still waiting")
        time.sleep(15)
        continue
