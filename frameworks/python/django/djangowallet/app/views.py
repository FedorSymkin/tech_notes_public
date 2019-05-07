# coding=utf-8

import coreapi
import coreschema

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.schemas import ManualSchema, AutoSchema
from rest_framework_csv.renderers import CSVRenderer
from rest_framework.settings import api_settings

from app import queries
from app import operations
from app import money_transfer
from app import models
from app import serializers


class CreateUserView(generics.GenericAPIView):

    """Register new user with wallet"""

    schema = AutoSchema(
        manual_fields=[
            coreapi.Field("currency", required=True, location="form", schema=coreschema.String()),
        ],
    )

    serializer_class = serializers.MyUserSerializer

    def post(self, request, *args, **kwargs):
        serializer = operations.create_user(request.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class GetUserView(generics.RetrieveAPIView):

    """Get user info by user id"""

    lookup_url_kwarg = 'user_id'
    lookup_field = 'id'
    queryset = models.MyUser.objects.all()
    serializer_class = serializers.MyUserSerializer


class GetUserByNameView(generics.RetrieveAPIView):

    """Get user info by username"""

    lookup_field = 'username'
    queryset = models.MyUser.objects.all()
    serializer_class = serializers.MyUserSerializer


class GetWalletView(generics.GenericAPIView):

    """Get wallet info (balance, currency)"""

    schema = ManualSchema(
        fields=[
            coreapi.Field("wallet_id", required=True, location="path", schema=coreschema.Integer()),
        ],
    )

    def get(self, request, *args, **kwargs):
        serializer = operations.get_wallet(kwargs.get('wallet_id'))
        return Response(serializer.data)


class CreateTransferOperationView(generics.GenericAPIView):

    """Create draft transfer operation from specified wallet to another one"""

    schema = ManualSchema(
        fields=[
            coreapi.Field("wallet_id", required=True, location="path", schema=coreschema.Integer()),
            coreapi.Field("wallet_to", required=True, location="form", schema=coreschema.Integer()),
            coreapi.Field("amount", required=True, location="form", schema=coreschema.Number()),
            coreapi.Field("currency", required=True, location="form", schema=coreschema.String()),
        ]
    )

    def post(self, request, *args, **kwargs):
        serializer = operations.create_transfer_operation(kwargs.get('wallet_id'), request.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CreatePutOperationView(generics.GenericAPIView):

    """Create put money operation from external source to specified wallet"""

    schema = ManualSchema(
        fields=[
            coreapi.Field("wallet_id", required=True, location="path", schema=coreschema.Integer()),
            coreapi.Field("amount", required=True, location="form", schema=coreschema.Number()),
            coreapi.Field("currency", required=True, location="form", schema=coreschema.String()),
        ]
    )

    def post(self, request, *args, **kwargs):
        serializer = operations.create_put_operation(kwargs.get('wallet_id'), request.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class SetOperationStatusView(generics.GenericAPIView):

    """Set operation status by operation id. It used by external payment gateway"""

    schema = ManualSchema(
        fields=[
            coreapi.Field("operation_id", required=True, location="path", schema=coreschema.Integer()),
            coreapi.Field("status", required=True, location="form", schema=coreschema.String()),
        ]
    )

    def patch(self, request, *args, **kwargs):
        serializer = money_transfer.set_operation_status(kwargs.get('operation_id'), request.data)
        return Response(serializer.data)


class GetOperationView(generics.RetrieveAPIView):

    """View transfer or put-money operation details"""

    lookup_field = 'id'
    lookup_url_kwarg = 'operation_id'
    serializer_class = serializers.OperationSerializer
    queryset = models.Operation.objects.all()


class WalletOperationsReportView(generics.ListAPIView):

    """Generate report of operations related to specified wallet"""

    schema = ManualSchema(
        fields=[
            coreapi.Field("wallet_id", required=True, location="path", schema=coreschema.Integer()),
            coreapi.Field("date_from", required=False, location="query", schema=coreschema.String()),
            coreapi.Field("date_to", required=False, location="query", schema=coreschema.String()),
            coreapi.Field("format", required=False, location="query", schema=coreschema.String()),
        ]
    )

    renderer_classes = tuple(api_settings.DEFAULT_RENDERER_CLASSES) + (CSVRenderer,)
    serializer_class = serializers.StatusChangeSerializer

    def get_queryset(self):
        return queries.get_wallet_report_queryset(self.kwargs.get('wallet_id'), self.request.GET)


class UsernameOperationsReportView(generics.ListAPIView):

    """Generate report of operations related to wallet of specified username"""

    schema = ManualSchema(
        fields=[
            coreapi.Field("username", required=True, location="path", schema=coreschema.String()),
            coreapi.Field("date_from", required=False, location="query", schema=coreschema.String()),
            coreapi.Field("date_to", required=False, location="query", schema=coreschema.String()),
            coreapi.Field("format", required=False, location="query", schema=coreschema.String()),
        ]
    )

    renderer_classes = tuple(api_settings.DEFAULT_RENDERER_CLASSES) + (CSVRenderer,)
    serializer_class = serializers.StatusChangeSerializer

    def get_queryset(self):
        return queries.get_username_report_queryset(self.kwargs.get('username'), self.request.GET)


class GetAllWalletsView(generics.ListAPIView):

    """Get all users wallets"""

    schema = ManualSchema(
        fields=[
            coreapi.Field("format", required=False, location="query", schema=coreschema.String()),
        ]
    )

    renderer_classes = tuple(api_settings.DEFAULT_RENDERER_CLASSES) + (CSVRenderer,)
    serializer_class = serializers.WalletSerializer
    queryset = models.Wallet.objects.all()
