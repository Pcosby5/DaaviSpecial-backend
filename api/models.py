from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid
from django.db.models import Sum, F

class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=255)
    street_address = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=255, blank=True, null=True)
    country = models.CharField(max_length=255, blank=True, null=True)
    USER_TYPE_CHOICES = [
        ('Customer', 'Customer'),
        ('Staff', 'Staff')
    ]
    user_type = models.CharField(max_length=50, choices=USER_TYPE_CHOICES)
    is_active = models.BooleanField(default=True)
    created_on = models.DateField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.username

class Customer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Customer: {self.user.username}'

class Staff(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Staff: {self.user.username}'

class Category(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

class Menu(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    description = models.CharField(max_length=255, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image_url = models.URLField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    def __str__(self):
        return self.description

class Order(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Processing', 'Processing'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled')
    ]
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Pending')

    def __str__(self):
        return f'Order {self.id} - {self.customer.user.username}'

    @property
    def total_price(self):
        total = self.items.aggregate(
            total_price=Sum(F('price') * F('quantity'))
        )['total_price']
        return total if total else 0

class OrderItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f'OrderItem {self.id} - {self.menu.description}'

class Payment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    PAYMENT_METHOD_CHOICES = [
        ('Credit Card', 'Credit Card'),
        ('Debit Card', 'Debit Card'),
        ('PayPal', 'PayPal'),
        ('MOMO', 'MOMO'),
        ('Cash', 'Cash')
    ]
    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHOD_CHOICES)
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Completed', 'Completed'),
        ('Failed', 'Failed')
    ]
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Payment {self.id} - {self.order.id}'

class Review(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField()
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Review {self.id} - {self.customer.user.username}'
