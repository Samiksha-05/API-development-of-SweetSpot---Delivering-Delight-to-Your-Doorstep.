import streamlit as st
import requests

def show(cake_id):
    # st.title("Cake Info")

    user_name = ""
    if st.session_state.user:
        user_id = st.session_state.user['user_id']
        response = requests.get(f"http://localhost:8000/api/customers/{user_id}/")
        if response.status_code == 200:
            user_data = response.json()
            user_name = user_data.get('first_name', "")

    # st.markdown(f"#### *🦉 Taste Happiness! <span style='color:#00FF00;'>{user_name}</span>?*",
    #             unsafe_allow_html=True)

    st.markdown(f"""
                <div style='text-align: left; font-size: 24px; font-weight: bold; margin-bottom: 20px; color: #DDDDDD; text-shadow: 2px 2px 4px #000000;'><i>
                    🦉 Taste Happiness! <span style='color:#00FF00;'>{user_name} ?</span></i>
                </div>
            """, unsafe_allow_html=True)

    # st.markdown("<hr>", unsafe_allow_html=True)

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

    col1, col_dummy, col2 = st.columns([1, 0.1, 2])

    with col1:
        st.markdown(f"""
            <div class="cake-box">
                <img src="{cake['image']}" class="cake-image">
            </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
            <div class="cake-details">
                <h3>{cake['name']} 🎂</h3>
                <p><strong>Description:</strong> {cake['description']}</p>
                <p><strong>Price:</strong> Rs.{cake['price']}</p>
                <p><strong>Size:</strong> {cake['size']}</p>
                <p><strong>Flavor:</strong> {cake['flavour']}</p>
            </div>
        """, unsafe_allow_html=True)

        # Add star rating
        rating = st.feedback(options="stars", key="cake_feedback")
        st.markdown(f"**Your Rating:** {rating} stars")

        col2_1, col2_2 = st.columns(2)
        with col2_1:
            if st.button("Add to Cart", key="add_to_cart", use_container_width=True):
                add_to_cart(cake_id)
        with col2_2:
            if st.button("Customize", key="customize", use_container_width=True):
                st.session_state.page = "customize"
                st.session_state.cake_id = cake_id
                st.rerun()

def add_to_cart(cake_id):
    if not st.session_state.user or 'user_id' not in st.session_state.user:
        st.error("You need to be logged in to add items to the cart.")
        return

    customer_id = st.session_state.user['user_id']
    data = {
        "customer": customer_id,
        "cake": cake_id,
        "quantity": 1,
        "customization": None
    }

    response = requests.post("http://localhost:8000/api/add-cake-to-cart/", json=data)

    if response.status_code in [200, 201]:
        st.toast("Added to cart!", icon="✅")
    else:
        st.toast("Failed to add to cart.", icon="⚠️")

if __name__ == "__main__":
    show(cake_id=1)