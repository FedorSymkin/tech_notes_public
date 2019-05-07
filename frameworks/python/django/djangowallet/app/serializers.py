from rest_framework import serializers

from app import models


class WalletSerializer(serializers.ModelSerializer):
    currency = serializers.SlugRelatedField(slug_field='name', queryset=models.Currency.objects.all())

    class Meta:
        model = models.Wallet
        fields = ('id', 'user', 'balance', 'currency')


class MyUserSerializer(serializers.ModelSerializer):
    wallet = WalletSerializer(read_only=True)

    class Meta:
        model = models.MyUser
        fields = ('id', 'username', 'password', 'country', 'city', 'wallet')

        extra_kwargs = {
            'password': {'write_only': True},
            'currency': {'write_only': True},
            'id': {'read_only': True},
        }


class OperationSerializer(serializers.ModelSerializer):
    currency = serializers.SlugRelatedField(slug_field='name', queryset=models.Currency.objects.all())
    status = serializers.SlugRelatedField(slug_field='status', read_only=True)
    currency_rate_wallet_from = serializers.ReadOnlyField()
    currency_rate_operation = serializers.ReadOnlyField()
    currency_rate_wallet_to = serializers.ReadOnlyField()

    class Meta:
        model = models.Operation
        fields = (
            'id', 'wallet_from', 'wallet_to', 'amount', 'currency',
            'currency_rate_wallet_from', 'currency_rate_operation',
            'currency_rate_wallet_to', 'status'
        )

    def save(self, **kwargs):
        if self.validated_data.get('wallet_from'):
            currency_rate_wallet_from = self.validated_data['wallet_from'].currency.rate
        else:
            currency_rate_wallet_from = None

        super().save(
            currency_rate_wallet_from=currency_rate_wallet_from,
            currency_rate_operation=self.validated_data['currency'].rate,
            currency_rate_wallet_to=self.validated_data['wallet_to'].currency.rate,
        )


class OperationStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.OperationStatus
        fields = ('operation', 'status')


class StatusChangeSerializer(serializers.ModelSerializer):
    operation = OperationSerializer()

    class Meta:
        model = models.StatusChange
        fields = ('datetime', 'operation', 'new_status')
