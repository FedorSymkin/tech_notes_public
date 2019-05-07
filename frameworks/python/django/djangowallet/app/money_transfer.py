from django.db import transaction

from rest_framework.exceptions import ValidationError, APIException

from app import models
from app.serializers import OperationStatusSerializer


ALLOWED_STATUS_CHANGES = {
    models.OperationStatus.Draft: {models.OperationStatus.Processing},
    models.OperationStatus.Processing: {models.OperationStatus.Accepted, models.OperationStatus.Failed},
    models.OperationStatus.Accepted: {},
    models.OperationStatus.Failed: {},
}


class NotEnoughMoneyError(Exception):
    pass


def validation_error_raiser(msg):
    def inner():
        raise ValidationError(msg)
    return inner


@transaction.atomic
def set_operation_status(operation_id, data) -> OperationStatusSerializer:
    new_status = data.get('status')
    if new_status not in ALLOWED_STATUS_CHANGES:
        raise ValidationError('bad status value: {}'.format(new_status))

    with models.lock_operation(operation_id) as operation:
        old_status = operation.status.status
        if old_status not in ALLOWED_STATUS_CHANGES:
            raise APIException('bad status in database: {}. Data for this operation is corrupted.'.format(old_status))

        if new_status not in ALLOWED_STATUS_CHANGES[old_status]:
            raise ValidationError('status change {} -> {} is not allowed'.format(old_status, new_status))

        try:
            move_money(operation, new_status)
            operation.status.status = new_status
            operation.status.save()
            return OperationStatusSerializer(operation.status)

        except NotEnoughMoneyError:
            operation.status.status = models.OperationStatus.Failed
            operation.status.save()
            transaction.on_commit(
                validation_error_raiser('Not enough money in wallet. Operation status set to failed')
            )


def move_money(operation, new_status):
    if new_status == models.OperationStatus.Processing:
        if operation.wallet_from:
            change_balance(
                wallet=operation.wallet_from,
                wallet_currency_rate=operation.currency_rate_wallet_from,
                amount=-operation.amount,
                amount_currency_rate=operation.currency_rate_operation
            )

    elif new_status == models.OperationStatus.Accepted:
        change_balance(
            wallet=operation.wallet_to,
            wallet_currency_rate=operation.currency_rate_wallet_to,
            amount=operation.amount,
            amount_currency_rate=operation.currency_rate_operation
        )

    elif new_status == models.OperationStatus.Failed:
        if operation.wallet_from:
            change_balance(
                wallet=operation.wallet_from,
                wallet_currency_rate=operation.currency_rate_wallet_from,
                amount=operation.amount,
                amount_currency_rate=operation.currency_rate_operation
            )


def change_balance(wallet, wallet_currency_rate, amount, amount_currency_rate):
    if not wallet:
        raise APIException('missing wallet, data corrupted')

    with models.lock_wallet(wallet.id):
        amount_in_base = amount * amount_currency_rate
        balance_in_base = wallet.balance * wallet_currency_rate
        new_balance_in_base = balance_in_base + amount_in_base
        if new_balance_in_base < 0:
            raise NotEnoughMoneyError()
        wallet.balance = new_balance_in_base / wallet_currency_rate
        wallet.save()
