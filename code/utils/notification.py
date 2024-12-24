from fastapi import HTTPException, status
from sib_api_v3_sdk.rest import ApiException
from typing import Literal
from config import setting
from twilio.rest import Client
import requests
import sib_api_v3_sdk

# This phone number is Twilio account phone number
SENDER_PHONE_NUMBER = "+15512136251"


def send_email(sender, to, subject, html_content) -> None:
    """
    sender: the format should be like {"name": "Info", "email": "info@mapmycrop.com"}
    to: the format should be like {"name": "Customer", "email": "customer@gmail.com"}
    subject: string
    html_content: html string
    """

    # Configure API key authorization: api-key
    configuration = sib_api_v3_sdk.Configuration()
    configuration.api_key["api-key"] = setting.SENDINBLUE_KEY

    # create an instance of the API class
    api_instance = sib_api_v3_sdk.TransactionalEmailsApi(
        sib_api_v3_sdk.ApiClient(configuration)
    )
    send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
        sender=sender, to=[to], subject=subject, html_content=html_content
    )

    try:
        api_response = api_instance.send_transac_email(send_smtp_email)
        return api_response
    except ApiException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=e)


def send_sms(contact: str, body: str):
    account_sid = setting.TWILIO_SID
    auth_token = setting.TWILIO_AUTH_TOKEN
    client = Client(account_sid, auth_token)

    message = client.messages.create(
        to="+" + contact, from_=SENDER_PHONE_NUMBER, body=body
    )
    # TODO: Remove print statement
    print(message)


def send_whatsapp(contact: str, name: str, title: str, body: str):
    url = "https://backend.aisensy.com/campaign/t1/api/v2"

    """
    compaignName: Aisensy campainName (not templateName)
    userName: receiver name
    destination: receiver whatsapp number
    templateParams: [{title}, {description}, {company name}]
    """

    payload = {
        "apiKey": setting.AISENSY_APIKEY,
        "campaignName": "apicampaign",
        "userName": name,
        "destination": "+" + contact,
        "templateParams": [title, body, "MMC"],
    }

    requests.post(url, json=payload)


def send_notification(
    type: Literal["WHATSAPP", "EMAIL", "SMS"],
    contact: str,
    name: str,
    title: str,
    body: str,
) -> None:
    if type == "EMAIL":
        sender = {"name": "Map My Crop", "email": "alerts@mapmycrop.com"}
        content = f"<html><body>{body}</body></html>"
        to = {"name": name, "email": contact}
        send_email(sender=sender, to=to, subject=title, html_content=content)

    elif type == "SMS":
        content = title + " \n " + body + "\n From " + name
        send_sms(contact, content)

    elif type == "WHATSAPP":
        send_whatsapp(contact, name, title, body)

    else:
        raise Exception("Type did not match any of the given values")
