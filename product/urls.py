from django.urls import path
from .views import *

urlpatterns = [
    path('create_product/', CreateProductView.as_view()),
    path('update_product/<int:pk>', UpdateProductView.as_view()),
]