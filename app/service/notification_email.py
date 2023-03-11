import base64
import os

from loguru import logger

from app.config import get_settings
from app.models.models import User
from app.models.shared_models import PublicUser

settings = get_settings()


class EmailNotification:
    def __init__(self):
        self.app_key = settings.email_mailjet_app_key
        self.secret_key = settings.email_mailjet_secret_key
        self.auth_header = self.generate_basic_auth(self.app_key, self.secret_key)

        self.sender = settings.email_sender
        self.base_url = settings.base_app_url
        self.product_name = "INTIO"

    def generate_basic_auth(self, username: str, password: str):
        return base64.b64encode(f"{username}:{password}".encode())

    # def send_by_email_labs(self, receiver: str, subject: str, template: str, vars: dict):
    #     url = "https://api.emaillabs.net.pl/api/sendmail_templates"
    #     smtp = settings.email_smtp
    #
    #     receiver_data = {f"to[{receiver}]": ""}
    #
    #     for key, value in vars.items():
    #         receiver_data[f"to[{receiver}][vars][{key}]"] = value
    #
    #     headers = {"Authorization": f"Basic {self.auth_header.decode()}"}
    #     template_data = {"from": self.sender, "smtp_account": smtp, "subject": subject, "template_id": template}
    #
    #     payload = receiver_data | template_data
    #     files = {}
    #
    #     response = request("POST", url, headers=headers, data=payload, files=files)
    #     return response.text

    def send_by_mailjet(self, payload: dict):
        if (os.getenv("TESTING") is not None) and (os.getenv("TESTING") == "1"):
            logger.info("Email test")
            return "TEST_EMAIL_NOTIFICATION"

        url = "https://api.mailjet.com/v3.1/send"
        headers = {"Content-Type": "application/json", "Authorization": f"Basic {self.auth_header.decode()}"}

        # pprint(payload)
        # response = request("POST", url, headers=headers, json=payload)
        #
        # return response.text

        return "OK"

    # MAILJET TEMPLATES COMMON

    def message_from_field(self):
        from_field = {"Email": "awaria@remontmaszyn.pl", "Name": "remontmaszyn.pl"}
        return from_field

    def message_to_field(self, user: User):
        email = user.email

        if settings.ENVIRONMENT != "PRD":
            email = settings.email_dev

        # to_field = [{"Email": "mail@outlook.com", "Name": f"{user.first_name} {user.last_name}"}]
        to_field = [{"Email": email, "Name": f"{user.first_name} {user.last_name}"}]
        return to_field

    def get_template_admin_registration(self, user: User, activation_url: str, debug: bool = False):
        message_dict = dict(
            From=self.message_from_field(),
            To=self.message_to_field(user),
            TemplateID=4561351,
            TemplateLanguage=True,
            Subject="Dziękuję za rejestrację",
            Variables={
                "product_name": self.product_name,
                "activation_url": self.base_url + activation_url,
                "login_url": self.base_url,
                "user_name": user.email,
            },
        )

        if debug:
            self.add_template_debugging(message_dict)

        return {"Messages": [message_dict]}

    def add_template_debugging(self, message_dict):
        message_dict["TemplateErrorReporting"] = {"Email": "m@m.pl", "Name": "Mailjet Template Errors"}

    def send_admin_registration(self, user: User | PublicUser, activation_url: str) -> None:
        data = self.get_template_admin_registration(user, activation_url, True)
        self.send_by_mailjet(data)
