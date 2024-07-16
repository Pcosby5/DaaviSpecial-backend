from rest_framework import serializers
from .models import User, Customer, Staff, Category, Menu, Order, OrderItem, Payment, Review

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'email', 'phone_number', 'street_address', 'city', 'country', 'user_type']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        # Ensure the user_type is set to 'customer' during user creation
        validated_data['user_type'] = 'Customer'
        user = User.objects.create_user(**validated_data)
        return user

class CustomerSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Customer
        fields = '__all__'

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user = UserSerializer.create(UserSerializer(), validated_data=user_data)
        customer = Customer.objects.create(user=user, **validated_data)
        return customer

class StaffSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Staff
        fields = '__all__'
        read_only_fields = ['user']

    # No create method to prevent staff registration through the API

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class MenuSerializer(serializers.ModelSerializer):
    class Meta:
        model = Menu
        fields = '__all__'

class OrderItemSerializer(serializers.ModelSerializer):
    order = serializers.PrimaryKeyRelatedField(queryset=Order.objects.all(), required=False)

    class Meta:
        model = OrderItem
        fields = '__all__'

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()
    delivery_method = serializers.CharField(source='get_delivery_method_display')

    class Meta:
        model = Order
        fields = ['id', 'customer', 'status', 'created_at', 'updated_at', 'items', 'total_price', 'delivery_method']

    def get_total_price(self, obj):
        return sum(item.price * item.quantity for item in obj.items.all())

class CreateOrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    delivery_method = serializers.ChoiceField(choices=Order.DELIVERY_METHOD_CHOICES)

    class Meta:
        model = Order
        fields = ['customer', 'items', 'delivery_method']

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        order = Order.objects.create(**validated_data)
        for item_data in items_data:
            OrderItem.objects.create(order=order, **item_data)
        return order

class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['id', 'order', 'amount', 'payment_method', 'status', 'created_at']
        read_only_fields = ['id', 'status', 'created_at']

class CreatePaymentSerializer(serializers.ModelSerializer):
    order_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = Payment
        fields = ['id', 'order_id', 'amount', 'payment_method', 'status', 'created_at']

    def create(self, validated_data):
        order_id = validated_data.pop('order_id')
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            raise serializers.ValidationError("Order not found")
        payment = Payment.objects.create(order=order, **validated_data)
        return payment

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = '__all__'
