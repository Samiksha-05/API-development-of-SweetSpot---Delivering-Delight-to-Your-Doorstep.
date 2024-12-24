from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import Customer, Cake, CakeCustomization, Cart, Order,Store

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'
        extra_kwargs = {
            'password': {'write_only': True},  # Ensure password is write-only
        }

    def validate_mobile_no(self, value):
        if not value.isdigit() or len(value) != 10:
            raise serializers.ValidationError("Invalid mobile number. It should be 10 digits.")
        return value

    def create(self, validated_data):
        # Hash the password using make_password
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)

class CakeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cake
        fields = ['id', 'name', 'flavour', 'size', 'price', 'description', 'image', 'available', 'store']


    def validate_price(self, value):
        try:
            float(value)  # Check if price can be converted to float
        except ValueError:
            raise serializers.ValidationError("Price must be a valid number")
        return value

    def get_image(self, obj):
        if obj.image:
            return self.context['request'].build_absolute_uri(obj.image.url)
        return None

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        request = self.context.get('request')
        if instance.image and request:
            representation['image'] = request.build_absolute_uri(instance.image.url)
        return representation

class CakeCustomizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CakeCustomization
        fields = '__all__'

class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = '__all__'

    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("Quantity must be a positive integer")
        return value

    def update(self, instance, validated_data):
        instance.quantity = validated_data.get('quantity', instance.quantity)
        instance.total_amount = validated_data.get('total_amount', instance.total_amount)
        instance.save()
        return instance

class OrderSerializer(serializers.ModelSerializer):
    items = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = '__all__'
        read_only_fields = ('total_price', 'order_date')  # Calculated fields

    def get_items(self, obj):
        cart_items = obj.items.all()
        detailed_items = []
        for cart_item in cart_items:
            cake = cart_item.cake.first()  # Assuming only one cake per cart item
            detailed_items.append({
                "cart_id": cart_item.id,
                "quantity": cart_item.quantity,
                "total_amount": float(cart_item.total_amount),
                "cake_id": cake.id,
                "cake_name": cake.name,
                "cake_price": float(cake.price),
                "customization": cart_item.customization.id if cart_item.customization else None
            })
        return detailed_items

    def validate_quantity(self, value):
        if not value.isdigit() or int(value) <= 0:
            raise serializers.ValidationError("Quantity must be a positive integer")
        return value

    def validate_delivery_address(self, value):
        if len(value) > 225:
            raise serializers.ValidationError("Delivery address is too long")
        return value


class StoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = '__all__'
    
    def validate_name(self, value):
        if len(value) < 3:
            raise serializers.ValidationError("Name is too short. It must be at least 3 characters long.")
        if len(value) > 100:
            raise serializers.ValidationError("Name is too long. It must be less than or equal to 100 characters.")
        return value

    def validate_city(self, value):
        if len(value) < 2:
            raise serializers.ValidationError("City name is too short. It must be at least 2 characters long.")
        if len(value) > 100:
            raise serializers.ValidationError("City name is too long. It must be less than or equal to 100 characters.")
        return value

    def validate_contact_number(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("Contact number must contain only digits.")
        if len(value) < 10 or len(value) > 15:
            raise serializers.ValidationError("Contact number must be between 10 and 15 digits.")
        return value

    def validate_email(self, value):
        if not serializers.EmailField().run_validation(value):
            raise serializers.ValidationError("Invalid email format.")
        return value

    def validate_description(self, value):
        if len(value) > 500:
            raise serializers.ValidationError("Description is too long. It must be less than or equal to 500 characters.")
        return value

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        request = self.context.get('request')
        if instance.store_image and request:
            representation['store_image'] = request.build_absolute_uri(instance.store_image.url)
        return representation
