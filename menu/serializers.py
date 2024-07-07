from rest_framework import serializers
from .models import Category, MenuItem

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']


class MenuItemSerializer(serializers.ModelSerializer):
    category_id = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), source='category')

    class Meta:
        model = MenuItem
        fields = ['id', 'name', 'description', 'price', 'image_url', 'category_id']
