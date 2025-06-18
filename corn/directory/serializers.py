from rest_framework import serializers
from .models import Products,OrderTable, OrderItem



class ProductsSerializers(serializers.ModelSerializer):
    class Meta:
        model = Products
        fields = ['id', 'name', 'price', 'category']

class OrderTableSerializers(serializers.ModelSerializer):
    class Meta:
        model = OrderTable
        fields = ['date', 'table', 'status']

class OrderItemSerializers(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['Order', 'product', 'count', 'price', 'sum']