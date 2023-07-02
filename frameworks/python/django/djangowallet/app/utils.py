import datetime

from django.conf import settings

from rest_framework.exceptions import ValidationError


def parse_user_date(src):
    try:
        return datetime.datetime.strptime(src, settings.QUERY_DATE_FORMAT) if src else None
    except Exception:
        raise ValidationError('bad date value: {}'.format(src))
