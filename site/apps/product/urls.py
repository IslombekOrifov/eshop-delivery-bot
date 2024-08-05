from django.urls import path

from .views import (
    CategoryView, ProductDetailView,
)

app_name = 'product'


urlpatterns = [
    path('category/<slug:slug>/<str:custom_id>/', CategoryView.as_view(), name='category'),
    path('detail/<slug:slug>/<str:custom_id>/', ProductDetailView.as_view(), name='detail'),
]
