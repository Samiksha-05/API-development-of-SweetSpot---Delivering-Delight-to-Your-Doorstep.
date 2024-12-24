import streamlit as st
import requests

def show():
    cake_id = st.session_state.get('cake_id')
    if not cake_id:
        st.error("No cake selected for customization.")
        return

    # Add custom CSS
    st.markdown("""
        <style>
        .cake-box {
            display: flex;
            flex-direction: column;
            align-items: center;
            border: 2px solid #2C2C2C;
            border-radius: 15px;
            padding: 20px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
            margin-bottom: 20px;
            background-color: #1a1a1a;  /* Added background color */
        }
        .cake-image {
            border-radius: 10px;
            width: 100%;
        }
        .cake-details {
            display: flex;
            flex-direction: column;
            justify-content: center;
            width: 100%;
            text-align: center;
        }
        .full-width-button {
            width: 100%;
            margin-top: 10px;
        }
        </style>
    """, unsafe_allow_html=True)

    response = requests.get(f"http://localhost:8000/api/cakes/{cake_id}/")
    if response.status_code == 200:
        cake = response.json()
    else:
        st.error("Failed to fetch cake details")
        return

    st.markdown("### Customize Your Cake")

    col1, col_dummy, col2 = st.columns([1, 0.1, 2])

    with col1:
        st.markdown(f"""
            <div class="cake-box">
                <img src="{cake['image']}" class="cake-image" alt="{cake['name']}">
                <div class="cake-details">
                    <h3>{cake['name']} 🍰</h3>
                    <p><strong>Flavor:</strong> {cake['flavour']}</p>
                </div>
            </div>
        """, unsafe_allow_html=True)

    with col2:
        with st.form(key='customization_form'):
            message = st.text_input("Message on cake")
            egg_version = st.selectbox("Egg version", ["With Egg", "Eggless"])
            toppings = st.multiselect("Toppings",
                                      ["Chocolate chips", "Sprinkles", "Nuts", "Fruits", "Caramel", "Marshmallows",
                                       "Oreo Crumbs", "Coconut Flakes", "M&Ms", "Gummy Bears"])
            shape = st.selectbox("Shape",
                                 ["Round", "Square", "Heart", "Triangle", "Star", "Hexagon", "Oval", "Rectangle"])

            col_submit, col_proceed = st.columns(2)
            with col_submit:
                submit_button = st.form_submit_button(label="Save Customization")
            with col_proceed:
                proceed_button = st.form_submit_button(label="Add to Cart")

            cancel_button = st.form_submit_button(label="Cancel")

        if submit_button:
            save_customization(cake_id, message, egg_version, toppings, shape)
        elif cancel_button:
            st.session_state.page = "cakes"
            st.rerun()
        elif proceed_button:
            customization_id = save_customization(cake_id, message, egg_version, toppings, shape)
            add_to_cart(cake_id, customization_id)

def save_customization(cake_id, message, egg_version, toppings, shape):
    if not st.session_state.user or 'user_id' not in st.session_state.user:
        st.error("You need to be logged in to save customization.")
        return None

    customer_id = st.session_state.user['user_id']
    data = {
        "message": message,
        "egg_version": egg_version,
        "toppings": ", ".join(toppings),
        "shape": shape,
        "cake": cake_id,
        "customer": customer_id
    }

    response = requests.post("http://localhost:8000/api/cake-customizations/", json=data)
    if response.status_code in [200, 201]:
        st.toast("Customization saved!", icon="✅")
        return response.json()['id']
    else:
        st.toast("Failed to save customization.", icon="❌")
        return None

def add_to_cart(cake_id, customization_id):
    if not st.session_state.user or 'user_id' not in st.session_state.user:
        st.error("You need to be logged in to add items to the cart.")
        return

    customer_id = st.session_state.user['user_id']
    data = {
        "customer": customer_id,
        "cake": cake_id,
        "quantity": 1,
        "customization": customization_id
    }

    response = requests.post("http://localhost:8000/api/add-cake-to-cart/", json=data)
    if response.status_code in [200, 201]:
        st.toast("Added to cart!", icon="✅")
        st.session_state.page = "cart"
        st.rerun()
    else:
        st.toast("Failed to add to cart.", icon="❌")

if __name__ == "__main__":
    show()