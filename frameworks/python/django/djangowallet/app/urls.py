from django.urls import path
from rest_framework.documentation import include_docs_urls
from . import views


urlpatterns = [
    path('', include_docs_urls(title='Simple Wallet API')),

    path('users/new/', views.CreateUserView.as_view()),
    path('users/<int:user_id>/', views.GetUserView.as_view()),

    path('wallets/<int:wallet_id>/', views.GetWalletView.as_view()),
    path('wallets/<int:wallet_id>/put_money/', views.CreatePutOperationView.as_view()),
    path('wallets/<int:wallet_id>/transfer/', views.CreateTransferOperationView.as_view()),
    path('wallets/<int:wallet_id>/operations/', views.WalletOperationsReportView.as_view()),
    path('wallets/all/', views.GetAllWalletsView.as_view()),

    path('operations/<int:operation_id>/', views.GetOperationView.as_view()),
    path('operations/<int:operation_id>/set_status/', views.SetOperationStatusView.as_view()),

    path('users/by_name/<str:username>/', views.GetUserByNameView.as_view()),
    path('users/by_name/<str:username>/operations/', views.UsernameOperationsReportView.as_view()),
]
