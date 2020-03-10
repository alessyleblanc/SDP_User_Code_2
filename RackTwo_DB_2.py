import boto3
from boto3.dynamodb.conditions import Key, Attr
import datetime
import json
import time
import math

import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522
#GPIO.cleanup()
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(2,GPIO.OUT)
GPIO.setup(4, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.setup(23,GPIO.OUT)
GPIO.setup(24, GPIO.IN, pull_up_down = GPIO.PUD_UP)
readerRFID = SimpleMFRC522()

dynamodb_resource = boto3.resource('dynamodb')
# dynamodb_client = boto3.client('dynamodb')
table = dynamodb_resource.Table('RackTwo_DB')  # Can change this to RackOne_DB or RackTwo_DB, depending on which Pi is used
currentItemCount = table.scan('count')['Count']  # 0 at beginning
endTime = datetime.datetime.now() + datetime.timedelta(0, 20, 0, 0,
                                                       0)  # days, seconds, micro-seconds, milli-seconds, minutes, hours
UserID = ''
infinityTime = 100000000 # 100,000,000 seconds = 3.1 years



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

def updateExpirationTime(item):
    global UserID
    global infinityTime
    newTime = int(item['ExpirationTime']) + infinityTime
    table.update_item(
        Key={
            'UserID': UserID,
            },
        UpdateExpression='SET ExpirationTime = :ttl',
        ExpressionAttributeValues={
            ':ttl': newTime
            }
    )


def deleteItem():
    table.delete_item(
        Key={
            'UserID': UserID
        }
    )


def checkTime(item):
    overTime = time.time() - (int(item['ExpirationTime']) - infinityTime)
    if(overTime > 300):
        fee = math.floor(overTime / 300)
        return fee
    
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
            elif (item['IsLocked'] == '0'):
                if (item['SpotNum'] == '1'):
                    print("SpotNum 1 is available to use now")
                    GPIO.output(2,GPIO.HIGH)  # Sets pin 18 to HIGH (used for solenoid)
                    while(True):
                        if(GPIO.input(4) == GPIO.LOW):
                            GPIO.output(2,GPIO.LOW)
                            break
                    updateIsLocked()
                    updateExpirationTime(item)
                elif (item['SpotNum'] == '2'):
                    print("SpotNum 2 is available to use now")
                    GPIO.output(23,GPIO.HIGH)  # Sets pin 23 to HIGH (used for solenoid)
                    while(True):
                        if(GPIO.input(24) == GPIO.LOW):
                            GPIO.output(23,GPIO.LOW)
                            break
                    updateIsLocked()
                    updateExpirationTime(item)
            elif (item['IsLocked'] == '1'):
                if (item['SpotNum'] == '1'):
                    print("You owe:", checkTime(item))
                    print("Spot 1 is now unlocked")
                    GPIO.output(2, GPIO.HIGH)  # Sets pin 17 to HIGH (used for solenoid)
                    time.sleep(10)
                    GPIO.output(2, GPIO.LOW)
                    deleteItem()
                elif (response['Item']['SpotNum'] == '2'):
                    print("You owe:", checkTime(item))
                    print("Spot 2 is now unlocked")
                    GPIO.output(23, GPIO.HIGH)  # Sets pin 17 to HIGH (used for solenoid)
                    time.sleep(10)
                    GPIO.output(23, GPIO.LOW)
                    deleteItem()
        except:
            print("Sorry, wrong UCard or no reservation in place for this UCard at the moment")
            continue


if __name__ == '__main__':
    main()