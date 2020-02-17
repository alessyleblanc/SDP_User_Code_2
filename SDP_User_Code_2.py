import boto3
import datetime
import json

# import RPi.GPIO as GPIO
# from mfrc522 import SimpleMFRC522

# GPIO.setmode(GPIO.BCM)
# GPIO.setup(18,GPIO.OUT)
# readerRFID = SimpleMFRC522()
# GPIO.setwarnings(False)

dynamodb_resource = boto3.resource('dynamodb')
# dynamodb_client = boto3.client('dynamodb')
table = dynamodb_resource.Table('RackTwo_DB')  # Can change this to RackOne_DB or RackTwo_DB, depending on which Pi is used
currentItemCount = table.scan('count')['Count']  # 0 at beginning
endTime = datetime.datetime.now() + datetime.timedelta(0, 20, 0, 0, 0)  # days, seconds, micro-seconds, milli-seconds, minutes, hours



# def readFromRFID():
#     #global userID
#     global readerRFID
#     id, text = readerRFID.read()
#     userID = text.strip()
#     return userID

def main():
    UserID = '30621276'  # readFromRFID()
    while (continueSearching):
        response = table.get_item(
            Key={
                'UserID': UserID
            }
        )
        try:
            item = response['Item']
            # if time limit reached, continue program and print ("Time limit reached, sorry")
            if(response['Item']['IsLocked'] == '0'):
                if(response['Item']['SpotNum'] == '1'):
                    print("SpotNum 1 is available to use now")
                    # GPIO.output(18, GPIO.HIGH)  # Sets pin 17 to HIGH (used for solenoid)
                    # while(True):
                    #   if(GPIO.input(17) == GPIO.LOW):
                    #       GPIO.output(18,GPIO.LOW)
                    # GPIO.cleanup()
                if(response['Item']['SpotNum'] == '2'):
                    print("SpotNum 2 is available to use now")
                    # GPIO.output(18, GPIO.HIGH)  # Sets pin 17 to HIGH (used for solenoid)
                    # while(True):
                    #   if(GPIO.input(17) == GPIO.LOW):
                    #       GPIO.output(18,GPIO.LOW)
                    # GPIO.cleanup()
            if(response['Item']['IsLocked'] == '1'):
                if (response['Item']['SpotNum'] == '1'):
                    print("Spot 1 is now unlocked")
                    # GPIO.output(18, GPIO.HIGH)  # Sets pin 17 to HIGH (used for solenoid)
                    # while(True):
                    #   if(GPIO.input(17) == GPIO.LOW):
                    #       GPIO.output(18,GPIO.LOW)
                    # GPIO.cleanup()
                    # table.delete_item(
                    #     Key={
                    #         'UserID': UserID
                    #     }
                    # )
                if(response['Item']['SpotNum'] == '2'):
                    print("Spot 2 is now unlocked")
                    # GPIO.output(18, GPIO.HIGH)  # Sets pin 17 to HIGH (used for solenoid)
                    # while(True):
                    #   if(GPIO.input(17) == GPIO.LOW):
                    #       GPIO.output(18,GPIO.LOW)
                    # GPIO.cleanup()
                    # table.delete_item(
                    #     Key={
                    #         'UserID': UserID
                    #     }
                    # )
        except:
            print("Sorry, wrong UCard or no reservation in place for this UCard at the moment")
            continue


if __name__ == '__main__':
    main()
