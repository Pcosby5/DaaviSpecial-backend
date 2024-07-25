from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserViewSet, CustomerViewSet, StaffViewSet, CategoryViewSet, MenuItemsByCategoryView,
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
    path('categories/<uuid:category_id>/menu-items/', MenuItemsByCategoryView.as_view(), name='menu-items-by-category'),
    path('orders/by-user/<uuid:user_id>/', OrderViewSet.as_view({'get': 'get_orders_by_user'}), name='orders-by-user'),
    path('payments/user-spec/<uuid:user_id>/', PaymentViewSet.as_view({'get': 'get_payments_by_user'}), name='payments-by-user'),
]
