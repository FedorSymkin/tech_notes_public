from contextlib import contextmanager

from django.db import models, transaction
from django.db.models.signals import post_save
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.core.validators import MinValueValidator
from django.dispatch import receiver
from django.http import Http404

from rest_framework.exceptions import ValidationError


def greater_than_zero_validator(value):
    if value <= 0:
        raise ValidationError('value must by strictly greater than 0')


class MyUser(AbstractUser):
    country = models.CharField(max_length=256)
    city = models.CharField(max_length=256)

    class Meta:
        indexes = [models.Index(fields=['username', ])]


class Currency(models.Model):
    name = models.CharField(max_length=3)
    rate = models.DecimalField(decimal_places=settings.DECIMAL_PLACES, max_digits=settings.DECIMAL_MAX_DIGITS)

    def __str__(self):
        return '<{}>'.format(self.name)


class Wallet(models.Model):
    user = models.OneToOneField(MyUser, on_delete=models.PROTECT, related_name='wallet', db_index=True)
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT)
    balance = models.DecimalField(
        decimal_places=settings.DECIMAL_PLACES,
        max_digits=settings.DECIMAL_MAX_DIGITS,
        default=0,
        validators=[MinValueValidator(0)],
    )

    def __str__(self):
        return '<{} {}>'.format(self.balance, self.currency)


class Operation(models.Model):
    wallet_from = models.ForeignKey(
        Wallet,
        on_delete=models.PROTECT,
        related_name='wallet_from',
        null=True,
        db_index=True
    )

    wallet_to = models.ForeignKey(
        Wallet,
        on_delete=models.PROTECT,
        related_name='wallet_to',
        db_index=True
    )

    amount = models.DecimalField(
        decimal_places=settings.DECIMAL_PLACES,
        max_digits=settings.DECIMAL_MAX_DIGITS,
        validators=[greater_than_zero_validator],
    )

    currency = models.ForeignKey(Currency, on_delete=models.PROTECT)

    currency_rate_wallet_from = models.DecimalField(
        decimal_places=settings.DECIMAL_PLACES,
        max_digits=settings.DECIMAL_MAX_DIGITS,
        validators=[greater_than_zero_validator],
        null=True
    )

    currency_rate_operation = models.DecimalField(
        decimal_places=settings.DECIMAL_PLACES,
        max_digits=settings.DECIMAL_MAX_DIGITS,
        validators=[greater_than_zero_validator],
    )
    currency_rate_wallet_to = models.DecimalField(
        decimal_places=settings.DECIMAL_PLACES,
        max_digits=settings.DECIMAL_MAX_DIGITS,
        validators=[greater_than_zero_validator],
    )


@receiver(post_save, sender=Operation)
def post_save_operation(sender, instance, created, **kwargs):
    if created:
        OperationStatus.objects.create(operation=instance)


class OperationStatus(models.Model):
    Draft, Processing, Accepted, Failed = 'draft', 'processing', 'accepted', 'failed'
    CHOICES = ((Draft, Draft), (Processing, Processing), (Accepted, Accepted), (Failed, Failed))

    operation = models.OneToOneField(Operation, on_delete=models.PROTECT, related_name='status', primary_key=True)
    status = models.CharField(max_length=10, choices=CHOICES, default=Draft)


@receiver(post_save, sender=OperationStatus)
def post_save_operation_status(sender, instance, **kwargs):
    StatusChange.objects.create(operation=instance.operation, new_status=instance.status)


class StatusChange(models.Model):
    operation = models.ForeignKey(Operation, on_delete=models.PROTECT, db_index=True)
    new_status = models.CharField(max_length=10)
    datetime = models.DateTimeField(default=timezone.now)


@transaction.atomic
@contextmanager
def lock_wallet(wallet_id):
    wallet = Wallet.objects.filter(id=wallet_id).select_for_update().first()
    if not wallet:
        raise Http404('wallet {} not found'.format(wallet_id))
    yield wallet


@transaction.atomic
@contextmanager
def lock_operation(operation_id):
    operation = Operation.objects.filter(id=operation_id).select_for_update().first()
    if not operation:
        raise Http404('operation {} not found'.format(operation_id))
    yield operation
