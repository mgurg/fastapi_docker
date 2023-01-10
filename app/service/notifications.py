from uuid import UUID

from app.models.models import Issue
from app.service.notification_email import EmailNotification


def notify_users(sms_list: list[dict], email_list: list[dict], issue: Issue = None):
    phones = []
    emails = []
    for sms in sms_list:
        if sms["phone"] is not None:
            phones.append(sms["phone"])

    for email in email_list:
        if email["email"] is not None:
            emails.append(email["email"])

    print(phones)
    print(emails)

    # bulk_email_send(emails, issue.name, issue.text, issue.uuid)


def bulk_email_send(receivers: list[str], name: str, description: str, url: UUID):

    receivers = ["ours86@gmail.com"]
    url = str(url)

    email = EmailNotification()
    template_data = {  # Template: b04fd986 	Failure_notification_PL
        "issue_name": name,
        "issue_description": description,
        "issue_url": "https://beta.remontmaszyn.pl/issues/" + url,
        "action_url": "https://beta.remontmaszyn.pl/issues/" + url,
        "product_name": "Intio",
        "sender_name": "Michał",
        "login_url": "https://beta.remontmaszyn.pl/login",
    }
    email.send(receivers, "[Intio] Nowe zgłoszenie " + name[0:20], "b04fd986", template_data)