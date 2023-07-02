from django.db import transaction
from rest_framework.generics import get_object_or_404

from app import models
from app.serializers import WalletSerializer, OperationSerializer, MyUserSerializer


@transaction.atomic
def create_user(data) -> MyUserSerializer:
    user_serializer = MyUserSerializer(data=data)
    user_serializer.is_valid(raise_exception=True)
    new_user = user_serializer.save()

    wallet_serializer = WalletSerializer(data={
        'user': new_user.id,
        'currency': data.get('currency')
    })
    wallet_serializer.is_valid(raise_exception=True)
    wallet_serializer.save()
    return user_serializer


def get_wallet(wallet_id) -> WalletSerializer:
    wallet = get_object_or_404(queryset=models.Wallet.objects.all(), id=wallet_id)
    return WalletSerializer(wallet)


@transaction.atomic
def create_transfer_operation(wallet_id, data) -> OperationSerializer:
    serializer = OperationSerializer(data={**data, 'wallet_from': wallet_id})
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return serializer


@transaction.atomic
def create_put_operation(wallet_id, data) -> OperationSerializer:
    serializer = OperationSerializer(data={**data, 'wallet_from': None, 'wallet_to': wallet_id})
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return serializer
