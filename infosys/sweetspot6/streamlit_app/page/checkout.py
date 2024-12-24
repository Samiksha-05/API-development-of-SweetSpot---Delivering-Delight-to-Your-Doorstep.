import streamlit as st
from streamlit_option_menu import option_menu
import requests
import time

def show(order_id):
    # st.title("Checkout")

    user_name = ""
    if st.session_state.user:
        user_id = st.session_state.user['user_id']
        response = requests.get(f"http://localhost:8000/api/customers/{user_id}/")
        if response.status_code == 200:
            user_data = response.json()
            user_name = user_data.get('first_name', "")

    st.markdown(f"#### *🛒 Ready to Checkout, <span style='color:#FF69B4;'>{user_name}</span>?*",
                unsafe_allow_html=True)

    # Fetch cart items
    if not st.session_state.user or 'user_id' not in st.session_state.user:
        st.error("You need to be logged in to proceed to checkout.")
        return

    customer_id = st.session_state.user['user_id']
    response = requests.get(f"http://localhost:8000/api/carts/?customer={customer_id}")
    if response.status_code == 200:
        cart_items = response.json()
    else:
        st.error("Failed to fetch cart items.")
        return

    # Calculate subtotal and total items
    subtotal = sum(float(item['total_amount']) for item in cart_items)
    total_items = sum(item['quantity'] for item in cart_items)
    discount = 0
    delivery_charges = 0
    total = subtotal - discount + delivery_charges

    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown(f"""
            <style>
            .cart-summary {{
                font-size: 18px;
                font-weight: bold;
                color: #FF69B4;
                # background-color: #2C2C2C;
                padding: 10px;
                border-radius: 10px;
                text-align: center;
            }}
            </style>
            <div class="cart-summary">
                🛒 You have {total_items} items in your cart
            </div>
        """, unsafe_allow_html=True)

        # Delivery address
        st.markdown("""
            <style>
            .delivery-address-box {
                font-size: 16px;
                font-weight: bold;
                color: #FF69B4;
                padding: 10px;
                border-radius: 10px;
                text-align: left;
                margin-bottom: 10px;
            }
            .delivery-address-label {
                color: #FF69B4;
                font-size: 16px;
                font-weight: bold;
                margin-bottom: 5px;
            }
            </style>
            <div class="delivery-address-label">
                Delivery Address
            </div>
        """, unsafe_allow_html=True)

        delivery_address = st.text_area("Enter your delivery address", key="delivery_address",
                                        placeholder="Enter your delivery address", height=80, max_chars=500,
                                        help="Please provide a detailed delivery address.",
                                        label_visibility="collapsed")

        # Payment method selection
        st.markdown("""
            <style>
            .payment-details-label {
                color: #FF69B4;
                font-size: 16px;
                font-weight: bold;
                margin-bottom: 5px;
            }
            </style>
            <div class="payment-details-label">
                Payment Details
            </div>
        """, unsafe_allow_html=True)
        payment_method = option_menu(
            None, ["Credit Card", "Debit Card", "Cash"],
            icons=['credit-card', 'credit-card', 'cash'],
            menu_icon="cast", default_index=0, orientation="horizontal"
        )

        with st.form(key='payment_form'):
            if payment_method in ["Credit Card", "Debit Card"]:
                card_number = st.text_input("Card Number")

                col1_1, col2_2 = st.columns(2)
                with col1_1:
                    card_expiry = st.text_input("Expiry Date (MM/YY)")
                with col2_2:
                    card_cvv = st.text_input("CVV", type="password")

                card_holder_name = st.text_input("Card Holder Name")
            elif payment_method == "Cash":
                st.markdown("**Cash on Delivery** selected. Please ensure you have the exact amount ready.")

            save_button = st.form_submit_button(label="Place Your Order", use_container_width=True)

        if save_button:
            if payment_method in ["Credit Card", "Debit Card"]:
                if not card_number or not card_expiry or not card_cvv or not card_holder_name:
                    st.error("Please fill in all card details.")
                    return

            order_id = st.session_state.get('order_id')
            # order_id = 27
            if not order_id:
                st.error("No order found. Please add items to the cart and proceed to checkout.")
                return

            # Update order with delivery address, payment details, and customer_id
            update_data = {
                "customer_id": customer_id,
                "delivery_address": delivery_address,
                "payment_method": payment_method.lower().replace(" ", "_"),
                "card_number": card_number if payment_method != "Cash" else None,
                "expiry_date": card_expiry if payment_method != "Cash" else None,
                "cvv": card_cvv if payment_method != "Cash" else None
            }
            update_response = requests.patch(f"http://localhost:8000/api/orders/{order_id}/", json=update_data)

            if update_response.status_code in [200, 204]:

                # st.write(update_data)
                # st.write(delivery_address)
                st.toast("Order Successfully Placed!", icon="✅")
                track_response = requests.get(f"http://localhost:8000/api/orders/delivery-tracking/{order_id}/")
                if track_response.status_code == 200:
                    st.toast("Order Tracking Started!", icon="✅")
                time.sleep(5)
                st.session_state.page = "home"
                st.rerun()
            else:
                st.error("Failed to save payment details.")
                st.error(update_response.json()['message'])
                # st.write(update_response.json())  # Log the response for debugging
                st.write(order_id)

    with col2:
        st.markdown("""
            <style>
            .order-summary-box {
                border: 1px solid #2C2C2C;
                border-radius: 10px;
                padding: 20px;
                background-color: #1a1a1a;
                color: white;
                margin-bottom: 8px;
            }
            </style>
        """, unsafe_allow_html=True)

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


if __name__ == "__main__":
    show(order_id=None)