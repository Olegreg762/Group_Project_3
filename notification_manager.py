from twilio.rest import Client
import os
from dotenv import load_dotenv


# loads variables from .env file
load_dotenv() 


def send_notification(message, user_number):
    # saves .env variables
    twilio_number = os.getenv("VIRTUAL_TWILIO_NUMBER")
    twilio_sid = os.getenv("TWILIO_SID")
    twilio_auth_token = os.getenv("TWILIO_AUTH_TOKEN")    

    # initializes client object
    client = Client(twilio_sid, twilio_auth_token)

    # creates and send notification message
    message = client.messages.create(
        body=message,
        from_=twilio_number,
        to=user_number
    )

