from app.config import get_settings
from app.models.models import Issue, User
from app.service.notification_email import EmailNotification

settings = get_settings()


def notify_users(sms_list: list[User], email_list: list[User], issue: Issue = None):
    print(">>> bulk_email_notification")
    email = EmailNotification()
    email.send_failure_notification(email_list, issue.name, issue.text, issue.uuid)


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i : i + n]
