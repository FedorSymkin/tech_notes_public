from django.db.models import Q, QuerySet

from rest_framework.generics import get_object_or_404

from app import models
from app import utils


def get_wallet_report_queryset(wallet_id, data) -> QuerySet:
    get_object_or_404(queryset=models.Wallet.objects.all(), id=wallet_id)

    res = models.StatusChange.objects.all().select_related('operation')
    res = res.filter(Q(operation__wallet_from=wallet_id) | Q(operation__wallet_to=wallet_id))

    date_from = utils.parse_user_date(data.get('date_from'))
    if date_from:
        res = res.filter(datetime__gte=date_from)

    date_to = utils.parse_user_date(data.get('date_to'))
    if date_to:
        res = res.filter(datetime__lte=date_to)

    res = res.order_by('-datetime')
    return res


def get_username_report_queryset(username, data) -> QuerySet:
    user = get_object_or_404(queryset=models.MyUser.objects.all(), username=username)
    return get_wallet_report_queryset(user.wallet.id, data)
