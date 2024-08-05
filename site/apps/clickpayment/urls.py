from django.urls import path
from . import views

urlpatterns = [
    path('transaction/create/', views.CreateClickTransactionView.as_view()),
    path('transaction/', views.ClickTransactionTestView.as_view()),
    path('service/<service_type>/', views.ClickMerchantServiceView.as_view())
]
