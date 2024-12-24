from rest_framework import viewsets, status, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth.hashers import check_password
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.parsers import JSONParser
from rest_framework.decorators import action
from django.utils import timezone
import sched, time, threading
from threading import Thread
from django.utils.timezone import now
from datetime import datetime,timedelta
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from .models import Customer, Cake, CakeCustomization, Cart, Order,Store # Notification
from .serializers import CustomerSerializer, CakeSerializer, CakeCustomizationSerializer, CartSerializer, OrderSerializer,StoreSerializer
import googlemaps
import re
import datetime
import logging
from rest_framework import permissions
from .permissions import IsAdminUser
from rest_framework.permissions import IsAuthenticated, AllowAny
# from rest_framework.decorators import api_view
# from django.shortcuts import get_object_or_404

logger = logging.getLogger(__name__)

scheduler = sched.scheduler(time.time, time.sleep)

def run_scheduler():
    while True:
        scheduler.run(blocking=False)
        time.sleep(1)


Thread(target=run_scheduler, daemon = True).start()

class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    parser_classes = (JSONParser,)


    @action(detail=False, methods=['post'])
    def login(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return Response({"status": False, "message": "Missing email or password"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = Customer.objects.get(email=email)
            if check_password(password, user.password):
                user_data = CustomerSerializer(user).data
                return Response({
                    "status": True,
                    "message": "Login successful",
                    "username": user_data['username'],
                    "user_id": user_data['id']  # Include user ID in the response
                }, status=status.HTTP_200_OK)
            else:
                return Response({"status": False, "message": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)
        except Customer.DoesNotExist:
            return Response({"status": False, "message": "User not found"}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['post'])
    def register(self, request):
        serializer = CustomerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"status": True, "message": "Registration successful", "data": serializer.data}, status=status.HTTP_201_CREATED)
        else:
            return Response({"status": False, "message": "Registration failed", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], url_path='get-by-email')
    def get_by_email(self, request):
        email = request.query_params.get('email')
        if not email:
            return Response({"message": "Email parameter is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            customer = Customer.objects.get(email=email)
            serializer = CustomerSerializer(customer)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Customer.DoesNotExist:
            return Response({"message": "Customer not found"}, status=status.HTTP_404_NOT_FOUND)


    @action(detail=False, methods=['post'], parser_classes=[MultiPartParser, FormParser])
    def update_profile_picture(self, request):
        customer_id = request.data.get('customer_id')
        profile_pic = request.data.get('profile_pic')

        if not customer_id or not profile_pic:
            return Response({"status": False, "message": "Missing customer ID or profile picture"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            customer = Customer.objects.get(id=customer_id)
            customer.profile_pic = profile_pic
            customer.save()
            return Response({"status": True, "message": "Profile picture updated successfully"}, status=status.HTTP_200_OK)
        except Customer.DoesNotExist:
            return Response({"status": False, "message": "Customer not found"}, status=status.HTTP_404_NOT_FOUND)


class CakeViewSet(viewsets.ModelViewSet):
    queryset = Cake.objects.all()
    serializer_class = CakeSerializer

    def get_serializer_context(self):
        return {'request': self.request}

class CakeCustomizationViewSet(viewsets.ModelViewSet):
    queryset = CakeCustomization.objects.all()
    serializer_class = CakeCustomizationSerializer

class CartViewSet(viewsets.ModelViewSet):
    queryset = Cart.objects.all()
    serializer_class = CartSerializer

    def get_queryset(self):
        customer_id = self.request.query_params.get('customer')
        if customer_id:
            return Cart.objects.filter(customer_id=customer_id)
        return super().get_queryset()

    def partial_update(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            return Response(serializer.data)
        except AttributeError as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AddCakeToCartViewSet(viewsets.ViewSet):
    def create(self, request, pk=None):
        customer_id = request.data.get('customer')
        cake_id = request.data.get('cake')
        quantity = request.data.get('quantity', 1)
        customization_id = request.data.get('customization')

        try:
            customer = Customer.objects.get(id=customer_id)
            cake = Cake.objects.get(id=cake_id)

            if customization_id:
                customization = CakeCustomization.objects.filter(id=customization_id, customer=customer, cake=cake).first()
                if not customization:
                    return Response({"message": "Invalid cake customization"}, status=status.HTTP_400_BAD_REQUEST)

            cart_item = Cart.objects.filter(customer=customer, cake=cake).first()
            if cart_item:
                # Update existing cart item
                cart_item.quantity += int(quantity)
                cart_item.total_amount = cake.price * cart_item.quantity
                if customization_id:
                    cart_item.customization = customization
                cart_item.save()
                serializer = CartSerializer(cart_item)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                # Create new cart item
                cart = Cart.objects.create(customer=customer, quantity=quantity, total_amount=cake.price * int(quantity))
                cart.cake.add(cake)
                if customization_id:
                    cart.customization = customization
                cart.save()
                serializer = CartSerializer(cart)
                return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Customer.DoesNotExist:
            return Response({"message": "Customer not found"}, status=status.HTTP_404_NOT_FOUND)
        except Cake.DoesNotExist:
            return Response({"message": "Cake not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def update(self, request, pk=None):
        return self.create(request)


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def retrieve(self, request, pk=None):
        try:
            order = self.get_object()
            serializer = self.get_serializer(order)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Order.DoesNotExist:
            return Response({"message": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

    @staticmethod
    def validate_card(card_number, expiration_date, cvv):
        def luhn_checksum(card_num):
            def digits_of(n):
                return [int(d) for d in str(n)]

            digits = digits_of(card_num)
            odd_digits = digits[-1::-2]
            even_digits = digits[-2::-2]
            checksum = sum(odd_digits)
            for d in even_digits:
                checksum += sum(digits_of(d * 2))
            return checksum % 10

        if luhn_checksum(card_number) != 0:
            return False, "Invalid card number"

        if not re.match(r"(0[1-9]|1[0-2])/[0-9]{2}", expiration_date):
            return False, "Invalid expiration date format. Expected MM/YY."

        exp_month, exp_year = expiration_date.split('/')
        exp_month = int(exp_month)
        exp_year = int(exp_year)
        current_year = datetime.datetime.now().year
        current_month = datetime.datetime.now().month


        if exp_year < 100:
            exp_year += 2000

        if exp_year < current_year or (exp_year == current_year and exp_month < current_month):
            return False, "Card expiration date is invalid or expired."

        if not re.match(r"^[0-9]{3,4}$", cvv):
            return False, "Invalid CVV."

        return True, "Card is valid"

    def create(self, request, *args, **kwargs):
        data = request.data
        customer_id = data.get('customer')
        cart_ids = data.get('items')
        delivery_address = data.get('delivery_address')
        order_status = data.get('status', 'Pending Payment')

        if not customer_id or not cart_ids or not delivery_address:
            return Response({"message": "Missing required fields"}, status=status.HTTP_400_BAD_REQUEST)

        total_price = 0
        total_quantity = 0
        cart_items = []

        try:
            for cart_id in cart_ids:
                cart = Cart.objects.get(id=cart_id)
                total_price += float(cart.total_amount)
                total_quantity += cart.quantity
                cart_items.append(cart)

            order = Order.objects.create(
                customer_id=customer_id,
                delivery_address=delivery_address,
                order_status=order_status,
                total_price=total_price,
                total_quantity=total_quantity
            )
            order.items.set(cart_items)
            order.save()

            serializer = self.get_serializer(order)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Customer.DoesNotExist:
            return Response({"message": "Customer not found"}, status=status.HTTP_404_NOT_FOUND)
        # except Cake.DoesNotExist:
        #     return Response({"message": "Cake not found"}, status=status.HTTP_404_NOT_FOUND)
        except Cart.DoesNotExist:
            return Response({"message": "Cart not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # except Customer.DoesNotExist:
        #     return Response({"message": "Customer not found"}, status=status.HTTP_404_NOT_FOUND)
        # except Cake.DoesNotExist:
        #     return Response({"message": "Cake not found"}, status=status.HTTP_404_NOT_FOUND)
        # except Cart.DoesNotExist:
        #     return Response({"message": "Cart not found"}, status=status.HTTP_404_NOT_FOUND)
        # except Exception as e:
        #     return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def partial_update(self, request, pk=None):
        # Fetch the order instance from the order id in the URL
        order_id = pk
        logger.debug(f"Order ID: {order_id}")
        try:
            order_instance = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return Response({"message": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

        # Get input fields from the request
        customer_id = request.data.get('customer_id')
        delivery_address = request.data.get('delivery_address')
        payment_method = request.data.get('payment_method')
        card_number = request.data.get('card_number')
        expiry_date = request.data.get('expiry_date')
        cvv = request.data.get('cvv')

        # Validate customer_id
        if not customer_id:
            return Response({"message": "Customer ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Fetch the customer and validate
        try:
            customer = Customer.objects.get(id=customer_id)
        except Customer.DoesNotExist:
            return Response({"message": "Customer not found"}, status=status.HTTP_400_BAD_REQUEST)

        # Fetch the cart
        cart_items = Cart.objects.filter(customer=customer)
        if not cart_items:
            return Response({"message": "Cart item not found for the specified customer"},
                            status=status.HTTP_404_NOT_FOUND)

        # Validate payment_method
        if payment_method not in ['debit_card', 'credit_card', 'cash']:
            return Response({"message": "Invalid payment method"}, status=status.HTTP_400_BAD_REQUEST)

        # Validate card details if payment method is not cash
        if payment_method != 'cash':
            if not card_number or not expiry_date or not cvv:
                return Response({"message": "Card details are required for non-cash payments"},
                                status=status.HTTP_400_BAD_REQUEST)
            is_valid, error_message = self.validate_card(card_number, expiry_date, cvv)
            if not is_valid:
                return Response({"message": f"{error_message}"}, status=status.HTTP_400_BAD_REQUEST)

        # Update order instance fields
        order_instance.payment_method = payment_method
        order_instance.payment_status = 'paid'
        order_instance.order_status = 'shipped'
        order_instance.delivery_address = delivery_address
        order_instance.order_date = timezone.now()
        order_instance.save()

        # Store cart items for the response
        cart_items_data = [{"cake_name": cake.name, "quantity": cart_item.quantity} for cart_item in cart_items for cake
                           in cart_item.cake.all()]

        # Sending confirmation mail to the customer's email
        cake_names = [cake['cake_name'] for cake in cart_items_data]
        subject = 'Congratulations! Your Order Has Been Placed'
        html_message = render_to_string('email.html', {
            'order_id': order_id,
            'customer_name': customer.first_name + ' ' + customer.last_name,
            'cake_names': ', '.join(cake_names),
        })
        plain_message = strip_tags(html_message)
        from_email = 'sweetspot297@gmail.com'
        to_email = [customer.email]

        send_mail(subject, plain_message, from_email, to_email, html_message=html_message)

        # Deleting the cart items
        for cart_item in cart_items:
            cart_item.delete()

        return Response({
            "status": "success",
            "order_status": order_instance.order_status,
            "payment_status": order_instance.payment_status,
            "customer_id": customer.id,
            "delivery_address": order_instance.delivery_address,
            "order_id": order_instance.id,
            "items": cart_items_data
        }, status=status.HTTP_200_OK)
    
    def schedule_mail(self, send_time, subject, message, recipient_list):
        delay = (send_time - now()).total_seconds()
        scheduler.enter(delay, 1, send_mail , argument=(subject, message, settings.EMAIL_HOST_USER, recipient_list))

    # @action(detail=False, methods=['GET'], url_path='delivery-tracking/(?P<id>[^/]+)')
    @action(detail=False, methods=['GET'], url_path='delivery-tracking/(?P<id>[^/]+)')
    def delivery_tracking(self, request, id):
        try:
            order = Order.objects.get(id=id)
        except Order.DoesNotExist:
            logger.error(f"Order with id {id} not found")
            return Response({"message": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

        try:
            gmaps = googlemaps.Client(key="Google API KEY")

            sweetspot_location = "Layers of Love, Kakinada, AndhraPradesh, India"
            delivery_location = order.delivery_address

            distance_matrix = gmaps.distance_matrix(sweetspot_location, delivery_location)

            if distance_matrix['status'] == 'OK':
                distance = distance_matrix['rows'][0]['elements'][0]['distance']['text']
                duration = distance_matrix['rows'][0]['elements'][0]['duration']['text']
                current_location = sweetspot_location  # Assuming the current location is the source for simplicity

                # Calculate delivery time and remainder time
                minutes = int(duration.split()[0])
                delivery_time = now() + timedelta(minutes=minutes)
                remainder_time = delivery_time - timedelta(minutes=5)

                # Schedule emails (if needed)
                self.schedule_mail(now(), f'Order Confirmation - Order ID: {id}',
                   f'Dear Valued Customer, we are delighted to confirm your order (ID: {id}). It is now being prepared with utmost care and is expected to arrive at {order.delivery_address} within {duration}. We appreciate the opportunity to serve you and assure you of our highest standards.',
                   [order.customer.email])
                self.schedule_mail(remainder_time, f'Reminder: Order ID: {id} - Delivery Imminent',
                   f'Dear Valued Customer, your order (ID: {id}) will be arriving shortly, within the next 5 minutes. We thank you for your patience and trust, and hope this delivery enhances your day.',
                   [order.customer.email])
                self.schedule_mail(delivery_time, f'Order ID: {id} - Successful Delivery',
                   f'Dear Valued Customer, we are pleased to inform you that your order (ID: {id}) has been successfully delivered to {order.delivery_address}. We hope it meets your expectations and adds a delightful experience to your day. Thank you for choosing us!',
                   [order.customer.email])


                return Response({
                    'order_id': id,
                    'from': sweetspot_location,
                    'to': delivery_location,
                    'current_location': current_location,
                    'distance': distance,
                    'duration': duration
                }, status=status.HTTP_200_OK)
            else:
                logger.error(f"Google Maps API error: {distance_matrix['status']}")
                return Response({"message": "API is not responding."}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.error(f"Internal server error: {str(e)}")
            return Response({"message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class PaymentView(APIView):
    def post(self, request):
        card_number = request.data.get('card_number')
        expiry_date = request.data.get('expiry_date')
        cvv = request.data.get('cvv')
        amount = request.data.get('amount')

        if not card_number or not expiry_date or not cvv or not amount:
            return Response({"message": "Missing payment details"}, status=status.HTTP_400_BAD_REQUEST)

        order_viewset = OrderViewSet()
        is_valid, validation_message = order_viewset.validate_card(card_number, expiry_date, cvv)
        if not is_valid:
            return Response({"message": validation_message}, status=status.HTTP_400_BAD_REQUEST)

        # Here you should add the actual payment processing logic
        payment_successful, payment_message = self.process_payment(card_number, expiry_date, cvv, amount)

        if payment_successful:
            return Response({"message": payment_message, "status": "success"}, status=status.HTTP_200_OK)
        else:
            return Response({"message": payment_message, "status": "failure"}, status=status.HTTP_400_BAD_REQUEST)

    def process_payment(self, card_number, expiry_date, cvv, amount):
        # This is a placeholder implementation
        success = True
        message = "Payment processed successfully" if success else "Payment failed"
        return success, message


class AdminCustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]



class AdminCakeViewSet(viewsets.ModelViewSet):
    queryset = Cake.objects.all()
    serializer_class = CakeSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.IsAdminUser()]
        return [IsAdminUser()]

class AdminCakeCustomizationViewSet(viewsets.ModelViewSet):
    queryset = CakeCustomization.objects.all()
    serializer_class = CakeCustomizationSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.IsAdminUser()]
        return [IsAdminUser()]


class AdminOrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.IsAdminUser()]
        return [IsAdminUser()]

class AdminStoreViewSet(viewsets.ModelViewSet):
    queryset = Store.objects.all()
    serializer_class = StoreSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get_permissions(self):
        if self.action == 'store_has_cakes':
            return [permissions.AllowAny()]
        return super().get_permissions()


    @action(detail=True, methods=['get'], url_path='store-has-cakes')
    def store_has_cakes(self, request, pk=None):
        try:
            store = Store.objects.get(pk=pk)
        except Store.DoesNotExist:
            return Response({"message": "Store not found"}, status=status.HTTP_404_NOT_FOUND)
        
        cakes = Cake.objects.filter(store=store)
        serializer = CakeSerializer(cakes, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['put'])
    def update_store(self, request, pk=None):
        try:
            store = Store.objects.get(pk=pk)
            serializer = StoreSerializer(store, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Store.DoesNotExist:
            return Response({"message": "Store not found"}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['get'])
    def retrieve_store(self, request, pk=None):
        try:
            store = Store.objects.get(pk=pk)
            serializer = StoreSerializer(store)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Store.DoesNotExist:
            return Response({"message": "Store not found"}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['get'])
    def search_stores(self, request):
        query = request.query_params.get('q', None)
        if query:
            stores = Store.objects.filter(name__icontains=query) | Store.objects.filter(city__icontains=query)
            serializer = StoreSerializer(stores, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({"message": "Query parameter is required"}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def filter_stores(self, request):
        city = request.query_params.get('city', None)
        if city:
            stores = Store.objects.filter(city=city)
            serializer = StoreSerializer(stores, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({"message": "City parameter is required"}, status=status.HTTP_400_BAD_REQUEST)



class UserStoreViewSet(viewsets.ModelViewSet):
    queryset = Store.objects.all()
    serializer_class = StoreSerializer
    permission_classes = [AllowAny]

    @action(detail=True, methods=['get'], url_path='cakes')
    def store_cakes(self, request, pk=None):
        try:
            store = Store.objects.get(pk=pk)
        except Store.DoesNotExist:
            return Response({"message": "Store not found"}, status=status.HTTP_404_NOT_FOUND)

        cakes = Cake.objects.filter(store=store)
        serializer = CakeSerializer(cakes, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

# @api_view(['GET'])
# def get_notifications(request):
#     notifications = Notification.objects.filter(user=request.user, is_read=False)
#     data = [{'message': n.message, 'created_at': n.created_at} for n in notifications]
#     return Response(data)
#
# from django.http import JsonResponse
#
# def update_order_status(request, order_id, status):
#     order = get_object_or_404(Order, id=order_id)
#     order.status = status
#     order.save()
#
#     Notification.objects.create(
#         user=order.customer.user,
#         message=f"Your order status has been updated to {order.get_status_display()}."
#     )
#
#     return JsonResponse({'message': 'Order status updated and notification sent.'})
