# API Documentation

## Authentication

### Obtain JWT Token
- **URL:** `POST /token/`
- **Request Body:**
  ```json
  {
    "username": "your_username",
    "password": "your_password"
  }
- **POST** `/token/refresh/`: Refresh JWT token.

## Customer APIs
- **POST** `/customers/register/`: Register a new customer.
- **POST** `/customers/login/`: Login a customer.
- **GET** `/customers/`: List all customers.
- **GET** `/customers/{id}/`: Retrieve a specific customer.
- **PUT** `/customers/{id}/`: Update a specific customer.
- **DELETE** `/customers/{id}/`: Delete a specific customer.

## Cake APIs
- **GET** `/cakes/`: List all cakes.
- **POST** `/cakes/`: Create a new cake.
- **GET** `/cakes/{id}/`: Retrieve a specific cake.
- **PUT** `/cakes/{id}/`: Update a specific cake.
- **DELETE** `/cakes/{id}/`: Delete a specific cake.

## Cake Customization APIs
- **GET** `/cake-customizations/`: List all cake customizations.
- **POST** `/cake-customizations/`: Create a new cake customization.
- **GET** `/cake-customizations/{id}/`: Retrieve a specific cake customization.
- **PUT** `/cake-customizations/{id}/`: Update a specific cake customization.
- **DELETE** `/cake-customizations/{id}/`: Delete a specific cake customization.

## Cart APIs
- **GET** `/carts/`: List all cart items.
- **POST** `/add-cake-to-cart/`: Add a cake to the cart.
- **GET** `/carts/{id}/`: Retrieve a specific cart item.
- **PUT** `/carts/{id}/`: Update a specific cart item.
- **DELETE** `/carts/{id}/`: Delete a specific cart item.

## Order APIs
- **GET** `/orders/`: List all orders.
- **POST** `/orders/`: Create a new order.
- **GET** `/orders/{id}/`: Retrieve a specific order.
- **PUT** `/orders/{id}/`: Update a specific order.
- **DELETE** `/orders/{id}/`: Delete a specific order.
- **GET** `/delivery-tracking/{id}/`: Track delivery of a specific order.

## Payment APIs
- **POST** `/payment/`: Validate and process payment details.

## Store APIs
- **GET** `/admin/stores/`: List all stores.
- **POST** `/admin/stores/`: Create a new store.
- **GET** `/admin/stores/{id}/`: Retrieve a specific store.
- **PUT** `/admin/stores/{id}/`: Update a specific store.
- **DELETE** `/admin/stores/{id}/`: Delete a specific store.
- **GET** `/admin/stores/{id}/store-has-cakes/`: List cakes available in a specific store.