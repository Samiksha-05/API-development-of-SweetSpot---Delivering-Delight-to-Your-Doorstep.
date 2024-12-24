# cart.py
import streamlit as st
import requests

def show():
    st.markdown(
        """
        <style>
            .stApp {
                background: linear-gradient(135deg, #f8e1f7, #f7e4cc);
                background-size: 400% 400%;
                animation: gradientBackground 15s ease infinite;
                color: #333333;
                font-family: 'Arial', sans-serif;
            }

            @keyframes gradientBackground {
                0% { background-position: 0% 50%; }
                50% { background-position: 100% 50%; }
                100% { background-position: 0% 50%; }
            }

            .cake-name {
                max-width: 150px;
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
                font-weight: bold;
                color: #FF69B4;
            }
            .small-button {
                padding: 2px 5px;
                font-size: 10px;
            }
            .order-summary-box {
                border: 1px solid #FF69B4;
                border-radius: 15px;
                padding: 20px;
                background-color: #ffffff;
                color: #333333;
                margin-bottom: 20px;
                box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
                transition: transform 0.3s;
            }
            .order-summary-box:hover {
                transform: scale(1.05);
            }
            .full-width-button {
                width: 100%;
            }
            .stButton button {
                font-size: 14px;
                padding: 8px 16px;
                background-color: #FF69B4;
                color: white;
                border: none;
                border-radius: 10px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                transition: background-color 0.3s;
            }
            .stButton button:hover {
                background-color: #e058a3;
            }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.markdown(f"""
        <div style='text-align: left; font-size: 28px; font-weight: bold; color: #FF69B4;'>
            Your Cart 🛒
        </div>
    """, unsafe_allow_html=True)

    if not st.session_state.user or 'user_id' not in st.session_state.user:
        st.error("You need to be logged in to view your cart.")
        return

    customer_id = st.session_state.user['user_id']

    response = requests.get(f"http://localhost:8000/api/carts/?customer={customer_id}")
    if response.status_code == 200:
        cart_items = response.json()
    else:
        st.toast("Failed to fetch cart items.", icon="❌")
        return

    subtotal = sum(float(item['total_amount']) for item in cart_items)
    discount = 0
    delivery_charges = 0
    total = subtotal - discount + delivery_charges

    col1, col2 = st.columns([7, 3])

    with col1:
        for item in cart_items:
            if not item['cake']:
                continue

            cake_id = item['cake'][0]
            cake_response = requests.get(f"http://localhost:8000/api/cakes/{cake_id}/")
            if cake_response.status_code == 200:
                cake = cake_response.json()
            else:
                st.toast(f"Failed to fetch details for cake ID {cake_id}", icon="❌")
                continue

            quantity = item['quantity']
            total_price = float(item['total_amount'])

            col1_1, col1_2, col1_3, col1_4, col1_5, col1_6 = st.columns([3, 4, 3, 2, 1, 1])

            with col1_1:
                st.image(cake['image'], width=100)
            with col1_2:
                st.markdown(f"<div class='cake-name'>{cake['name']}</div>", unsafe_allow_html=True)
            with col1_3:
                new_quantity = st.number_input(
                    f"Quantity",
                    min_value=1,
                    value=quantity,
                    key=f"quantity_{item['id']}"
                )
                if new_quantity != quantity:
                    update_quantity(item['id'], new_quantity)
            with col1_4:
                st.markdown(f"<div style='text-align: center;'>₹{total_price:.2f}</div>", unsafe_allow_html=True)
            with col1_5:
                if st.button("🗑", key=f"remove_{item['id']}", help="Remove"):
                    remove_from_cart(item['id'])
            with col1_6:
                if st.button("🛠️", key=f"view_customization_{item['id']}", help="Customization"):
                    view_customization(item['customization'])

    with col2:
        with st.form(key='order_summary_form'):
            st.markdown(f"""
                <div class="order-summary-box">
                    <h3>Order Summary</h3>
                    <hr>
                    <p><strong>Subtotal:</strong> ₹{subtotal:.2f}</p>
                    <p><strong>Offers/Discounts:</strong> ₹{discount:.2f}</p>
                    <p><strong>Delivery Charges:</strong> ₹{delivery_charges:.2f}</p>
                    <hr>
                    <h5><strong>Total:</strong> ₹{total:.2f}</h5>
                </div>
            """, unsafe_allow_html=True)
            proceed_checkout = st.form_submit_button("Proceed to Checkout", use_container_width=True)

        if proceed_checkout:
            order_id = create_order(customer_id, cart_items, "Kolhapur")
            if order_id:
                st.session_state.order_id = order_id
                st.session_state.page = "checkout"
                st.rerun()
            else:
                st.toast("Failed to create order.", icon="❌")

def create_order(customer_id, cart_items, delivery_address):
    order_data = {
        "customer": customer_id,
        "items": [item['id'] for item in cart_items],
        "delivery_address": delivery_address,
        "status": "Pending Payment"
    }

    response = requests.post("http://localhost:8000/api/orders/", json=order_data)
    if response.status_code in [200, 201]:
        return response.json()['id']
    else:
        return None

def update_quantity(cart_item_id, new_quantity):
    if new_quantity < 1:
        st.toast("Quantity must be at least 1.", icon="⚠️")
        return

    cart_item_response = requests.get(f"http://localhost:8000/api/carts/{cart_item_id}/")
    if cart_item_response.status_code != 200:
        st.toast("Failed to fetch cart item details.", icon="❌")
        return

    cart_item = cart_item_response.json()
    cake_id = cart_item['cake'][0]
    cake_response = requests.get(f"http://localhost:8000/api/cakes/{cake_id}/")
    if cake_response.status_code != 200:
        st.toast("Failed to fetch cake details.", icon="❌")
        return

    cake = cake_response.json()
    new_total_amount = float(cake['price']) * new_quantity

    data = {"quantity": new_quantity, "total_amount": new_total_amount}
    response = requests.patch(f"http://localhost:8000/api/carts/{cart_item_id}/", json=data)

    if response.status_code in [200, 201]:
        st.toast("Quantity and total price updated!", icon="✅")
        st.rerun()
    else:
        st.toast("Failed to update quantity and total price.", icon="❌")

def remove_from_cart(cart_item_id):
    response = requests.delete(f"http://localhost:8000/api/carts/{cart_item_id}/")

    if response.status_code == 204:
        st.toast("Item removed from cart!", icon="✅")
        st.rerun()
    else:
        st.toast("Failed to remove item from cart.", icon="❌")

@st.dialog("Your Customization :")
def view_customization(customization_id):
    response = requests.get(f"http://localhost:8000/api/cake-customizations/{customization_id}/")
    if response.status_code == 200:
        customization = response.json()
        st.markdown(f"**Message:** {customization['message']}")
        st.markdown(f"**Egg Version:** {customization['egg_version']}")
        st.markdown(f"**Toppings:** {customization['toppings']}")
        st.markdown(f"**Shape:** {customization['shape']}")
    else:
        st.toast("Failed to fetch customization details.", icon="❌")

if __name__ == "__main__":
    show()
