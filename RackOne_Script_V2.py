import boto3
from boto3.dynamodb.conditions import Key, Attr
import datetime
import json
import time

import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522

GPIO.setmode(GPIO.BCM)
GPIO.setup(18, GPIO.OUT)
readerRFID = SimpleMFRC522()
GPIO.setwarnings(False)

dynamodb_resource = boto3.resource('dynamodb')
# dynamodb_client = boto3.client('dynamodb')
table = dynamodb_resource.Table('RackOne_DB')  # Can change this to RackOne_DB or RackTwo_DB, depending on which Pi is used
currentItemCount = table.scan('count')['Count']  # 0 at beginning
endTime = datetime.datetime.now() + datetime.timedelta(0, 20, 0, 0,
                                                       0)  # days, seconds, micro-seconds, milli-seconds, minutes, hours
UserID = ''
infinityTime = int(time.time()*10)



def readFromRFID():
    # global userID
    global readerRFID
    id, text = readerRFID.read()
    userID = text.strip()
    time.sleep(3)
    return userID


def updateIsLocked():
    global UserID
    table.update_item(
        Key={
            'UserID': UserID
        },
        UpdateExpression='SET #taskName = :r',
        ExpressionAttributeNames={
            '#taskName': 'IsLocked',
        },
        ExpressionAttributeValues={
            ':r': '1'
        }
    )

def updateExpirationTime():
    global UserID
    global infinityTime
    table.update_item(
        Key={
            'UserID': UserID,
            },
        UpdateExpression='SET ExpirationTime = :ttl',
        ExpressionAttributeValues={
            ':ttl': infinityTime
            }
    )


def deleteItem():
    table.delete_item(
        Key={
            'UserID': UserID
        }
    )


def main():
    global UserID
    while (True):
        UserID = readFromRFID()
        response = table.get_item(
            Key={
                'UserID': UserID
            }
        )
        try:
            item = response['Item']
            # startTime = datetime.datetime.strptime(item['SubmissionTime'], '%m/%d/%Y %H:%M:%S')
            ExpirationTime = item['ExpirationTime']
            if(time.time() > ExpirationTime):
                print("Your reservation is expired, please reserve again")
                # update whether reservation is expired
                # if statement whether user got the notice that their reservation expired
                deleteItem()
                GPIO.cleanup()
            elif (item['IsLocked'] == '0'):
                if (item['SpotNum'] == '1'):
                    print("SpotNum 1 is available to use now")
                    # GPIO.output(18, GPIO.HIGH)  # Sets pin 17 to HIGH (used for solenoid)
                    # while(True):
                    #   if(GPIO.input(17) == GPIO.LOW):
                    #       GPIO.output(18,GPIO.LOW)
                    updateIsLocked()
                    updateExpirationTime()
                    GPIO.cleanup()
                elif (item['SpotNum'] == '2'):
                    print("SpotNum 2 is available to use now")
                    # GPIO.output(18, GPIO.HIGH)  # Sets pin 17 to HIGH (used for solenoid)
                    # while(True):
                    #   if(GPIO.input(17) == GPIO.LOW):
                    #       GPIO.output(18,GPIO.LOW)
                    updateIsLocked()
                    updateExpirationTime()
                    GPIO.cleanup()
            elif (item['IsLocked'] == '1'):
                if (item['SpotNum'] == '1'):
                    print("Spot 1 is now unlocked")
                    # GPIO.output(18, GPIO.HIGH)  # Sets pin 17 to HIGH (used for solenoid)
                    # while(True):
                    #   if(GPIO.input(17) == GPIO.LOW):
                    #       GPIO.output(18,GPIO.LOW)
                    deleteItem()
                    GPIO.cleanup()
                elif (response['Item']['SpotNum'] == '2'):
                    print("Spot 2 is now unlocked")
                    # GPIO.output(18, GPIO.HIGH)  # Sets pin 17 to HIGH (used for solenoid)
                    # while(True):
                    #   if(GPIO.input(17) == GPIO.LOW):
                    #       GPIO.output(18,GPIO.LOW)
                    deleteItem()
                    GPIO.cleanup()
        except:
            print("Sorry, wrong UCard or no reservation in place for this UCard at the moment")
            GPIO.cleanup()
            continue


if __name__ == '__main__':
    main()