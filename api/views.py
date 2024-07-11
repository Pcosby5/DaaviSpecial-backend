from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import User, Customer, Staff, Category, Menu, Order, OrderItem, Payment, Review
from .serializers import (
    UserSerializer, CustomerSerializer, StaffSerializer, CategorySerializer,
    MenuSerializer, OrderSerializer, OrderItemSerializer, PaymentSerializer,
    CreatePaymentSerializer, ReviewSerializer, CreateOrderSerializer)
from rest_framework.decorators import action
from django.conf import settings
import requests
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json
import uuid

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def perform_create(self, serializer):
        serializer.save()

class StaffViewSet(viewsets.ModelViewSet):
    queryset = Staff.objects.all()
    serializer_class = StaffSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'put', 'patch', 'delete']

    # Prevent staff registration through the API by disabling POST
    def create(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class MenuViewSet(viewsets.ModelViewSet):
    queryset = Menu.objects.all()
    serializer_class = MenuSerializer

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = CreateOrderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def add_items(self, request, pk=None):
        order = self.get_object()
        items_data = request.data.get('items', [])
        for item_data in items_data:
            item_data['order'] = order.id
            item_serializer = OrderItemSerializer(data=item_data)
            item_serializer.is_valid(raise_exception=True)
            item_serializer.save()
        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)

class OrderItemViewSet(viewsets.ModelViewSet):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer

def get_access_token():
    url = "https://sandbox.momodeveloper.mtn.com/collection/token/"
    headers = {
        "Ocp-Apim-Subscription-Key": settings.MOMO_SUBSCRIPTION_KEY,
    }
    response = requests.post(url, headers=headers, auth=(settings.MOMO_USER_ID, settings.MOMO_API_KEY))
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        raise Exception("Failed to get access token")

class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = CreatePaymentSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        payment = serializer.save()
        return Response(self.get_serializer(payment).data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'])
    def initiate_payment(self, request):
        order_id = request.data.get('order_id')
        amount = request.data.get('amount')
        phone_number = request.data.get('phone_number')
        payment_method = request.data.get('payment_method')

        if not order_id or not amount or not phone_number or not payment_method:
            return Response({
                "error": "Order ID, amount, phone number, and payment method are required."}, status=status.HTTP_400_BAD_REQUEST)

        # Ensure the order exists
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return Response({"error": "Order not found."}, status=status.HTTP_404_NOT_FOUND)

        # Create the payment object with status 'Pending'
        payment = Payment.objects.create(order=order, amount=amount, payment_method=payment_method, status='Pending')

        # Prepare the data to be sent to the Mobile Money API
        access_token = get_access_token()
        url = 'https://sandbox.momodeveloper.mtn.com/collection/v1_0/requesttopay'
        reference_id = str(uuid.uuid4())
        headers = {
            'Authorization': f'Bearer {access_token}',
            'X-Reference-Id': reference_id,
            'X-Target-Environment': 'sandbox',
            'Ocp-Apim-Subscription-Key': settings.MOMO_SUBSCRIPTION_KEY,
            'Content-Type': 'application/json',
        }
        payload = {
            'amount': str(amount),
            'currency': 'GHS',
            'externalId': str(order.id),
            'payer': {
                'partyIdType': 'MSISDN',
                'partyId': phone_number
            },
            'payerMessage': 'Payment for Order',
            'payeeNote': 'Thank you for your order'
        }

        try:
            response = requests.post(url, headers=headers, json=payload)
            response_data = response.json()
            if response.status_code == 202:  # Status 202 indicates the request has been accepted
                payment.transaction_id = reference_id
                payment.save()
                return Response({
                    "payment_id": payment.id,
                    "transaction_id": reference_id,
                    "status": payment.status,
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({"error": response_data.get('message', 'Payment initiation failed.')}, status=status.HTTP_400_BAD_REQUEST)
        except requests.RequestException as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'])
    def success(self, request, pk=None):
        payment = self.get_object()
        order = payment.order

        payment.status = 'Completed'
        payment.save()

        order.status = 'Completed'
        order.save()

        return Response(PaymentSerializer(payment).data, status=status.HTTP_200_OK)

@csrf_exempt
def momo_callback(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        transaction_id = data.get('transaction_id')
        status = data.get('status')

        try:
            payment = Payment.objects.get(transaction_id=transaction_id)
            if status == 'success':
                payment.status = 'Completed'
            else:
                payment.status = 'Failed'
            payment.save()
            return JsonResponse({"message": "Payment status updated."}, status=200)
        except Payment.DoesNotExist:
            return JsonResponse({"error": "Payment not found."}, status=404)

    return JsonResponse({"error": "Invalid request method."}, status=400)

class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticated]

class LogoutView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        try:
            refresh_token = request.data['refresh_token']
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Successfully logged out."}, status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
