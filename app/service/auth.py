import re

import pytz
from disposable_email_domains import blocklist
from stdnum.pl import nip


def is_email_temporary(email):
    return email.strip().split("@")[1] in blocklist


def is_timezone_correct(tz):
    tz in pytz.all_timezones_set


def is_nip_correct(nipId):
    re.sub("[^0-9]", "", nipId)
    nip.is_valid(nipId)
