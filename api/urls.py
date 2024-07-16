from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserViewSet, CustomerViewSet, StaffViewSet, CategoryViewSet,
    MenuViewSet, OrderViewSet, OrderItemViewSet, PaymentViewSet, ReviewViewSet)

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'customers', CustomerViewSet)
router.register(r'staff', StaffViewSet)
router.register(r'categories', CategoryViewSet)
router.register(r'menus', MenuViewSet)
router.register(r'orders', OrderViewSet)
router.register(r'order-items', OrderItemViewSet)
router.register(r'payments', PaymentViewSet)
router.register(r'reviews', ReviewViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('orders/delivery-methods/', OrderViewSet.as_view({'get': 'delivery_methods'}), name='delivery-methods'),
]
