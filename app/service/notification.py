import base64
from pprint import pprint

from requests import request

from app.config import get_settings

settings = get_settings()


class EmailNotification:
    def __init__(self, app_key: str, secret_key: str, smtp: str):
        self.auth_header = base64.b64encode(f"{app_key}:{secret_key}".encode())
        self.url = "https://api.emaillabs.net.pl/api/sendmail_templates"
        self.smtp = smtp

    def send(self, sender: str, receiver: str, subject: str, template: str, vars: dict):

        if settings.environment != "production":
            receiver = settings.email_dev

        receiver_data = {f"to[{receiver}]": ""}

        for key, value in vars.items():
            receiver_data[f"to[{receiver}][vars][{key}]"] = value

        headers = {"Authorization": f"Basic {self.auth_header.decode()}"}
        template_data = {
            "from": sender,
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

        response = request("POST", self.url, headers=headers, data=payload, files=files)

        # print(response.text)
        # pprint(payload)

        return response.text
