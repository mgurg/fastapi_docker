import base64
import os

from requests import request

from app.config import get_settings

settings = get_settings()


class EmailNotification:
    def __init__(self):
        self.app_key = settings.email_labs_app_key
        self.secret_key = settings.email_labs_secret_key
        self.smtp = settings.email_smtp
        self.auth_header = base64.b64encode(f"{self.app_key}:{self.secret_key}".encode())
        self.url = "https://api.emaillabs.net.pl/api/sendmail_templates"
        self.sender = settings.email_sender

    def send(self, receiver: str, subject: str, template: str, vars: dict):

        if (os.getenv("TESTING") is not None) and (os.getenv("TESTING") == "1"):
            return "TEST_EMAIL_NOTIFICATION"

        if settings.ENVIRONMENT != "PRD":
            receiver = settings.email_dev

        receiver_data = {f"to[{receiver}]": ""}

        for key, value in vars.items():
            receiver_data[f"to[{receiver}][vars][{key}]"] = value

        headers = {"Authorization": f"Basic {self.auth_header.decode()}"}
        template_data = {
            "from": self.sender,
            "smtp_account": self.smtp,
            "subject": subject,
            "template_id": template,
        }

        payload = receiver_data | template_data
        files = {}

        # data = {
        # "to[email@domain.com]": "",
        # "smtp_account": "1.account.smtp",
        # "subject": "Test template 2",
        # "html": "Some HTML",
        # "text": "Some Text",
        # "reply_to": "reply@domain.com",
        # "from": "from_address@domain.com",
        # "from_name": "Office",
        #  'files[0][name]' : "name.png",
        #  'files[0][mime]' : "image/png",
        #  'files[0][content]' : base64.b64encode(file_get_contents("grafika.png")),
        # }

        # print(response.text)
        # pprint(payload)

        response = request("POST", self.url, headers=headers, data=payload, files=files)
        return response.text
