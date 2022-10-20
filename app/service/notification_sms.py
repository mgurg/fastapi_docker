import base64
import os

from requests import request

from app.config import get_settings

settings = get_settings()


class SMSNotification:
    def __init__(self):
        self.app_key = settings.email_labs_app_key
        self.secret_key = settings.email_labs_secret_key
        self.smtp = ""
        self.auth_header = base64.b64encode(f"{self.app_key}:{self.secret_key}".encode())
        self.url = "https://api.emaillabs.net.pl/api/sendmail_templates"
        self.smtp = settings.email_smtp

    def send(self, sender: str, receiver: list, message: str, template: str):

        if settings.ENVIRONMENT != "PRD":
            receiver = settings.email_dev

        receiver_data = {f"to[{receiver}]": ""}

        for key, value in vars.items():
            receiver_data[f"to[{receiver}][vars][{key}]"] = value

        headers = {"Authorization": f"Basic {self.auth_header.decode()}"}
        template_data = {
            "from": sender,
            "smtp_account": self.smtp,
            "subject": "subject",
            "template_id": template,
        }

        payload = receiver_data | template_data
        files = {}

        if (os.getenv("TESTING") is not None) and (os.getenv("TESTING") == "1"):
            return "TEST_EMAIL_NOTIFICATION"

        # print(response.text)
        # pprint(payload)

        response = request("POST", self.url, headers=headers, data=payload, files=files)
        return response.text
