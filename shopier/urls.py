from django.urls import path
from . import views

urlpatterns = [
    path('order/', views.order_form_view, name='order_form'),
    path('payment/', views.shopier_payment_post, name='shopier_payment'),
    path('callback/', views.shopier_callback, name='shopier_callback'),  # Yeni eklendi
]
