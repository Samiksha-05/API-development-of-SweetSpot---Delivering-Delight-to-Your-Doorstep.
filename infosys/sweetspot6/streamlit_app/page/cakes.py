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
        </style>
        """,
        unsafe_allow_html=True
    )

    user_name = ""
    if st.session_state.user:
        user_id = st.session_state.user['user_id']
        response = requests.get(f"http://localhost:8000/api/customers/{user_id}/")
        if response.status_code == 200:
            user_data = response.json()
            user_name = user_data.get('first_name', "")

    st.markdown(f"""
            <div style='text-align: center; font-size: 28px; font-weight: bold; margin-bottom: 30px; color: #FF69B4;'>
                What's Your Sweet Craving Today, <span style='color:#800080;'>{user_name}</span>?
            </div>
        """, unsafe_allow_html=True)

    st.markdown("""
        <style>
        .cake-box {
            background-color: #ffffff;
            border-radius: 20px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
            text-align: center;
            transition: transform 0.3s;
        }
        .cake-box:hover {
            transform: scale(1.05);
        }
        .cake-details {
            background-color: #f0f0f0;
            border-radius: 10px;
            padding: 10px;
            margin-top: 10px;
            text-align: center;
            position: relative;
        }
        .cake-name {
            color: #FF69B4;
            white-space: nowrap;
            font-size: 18px;
            overflow: hidden;
            text-overflow: ellipsis;
            margin-bottom: 5px;
            font-weight: bold;
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
    """, unsafe_allow_html=True)

    response = requests.get("http://localhost:8000/api/cakes/")
    if response.status_code == 200:
        cakes = response.json()
    else:
        st.error("Failed to fetch cakes data")
        return

    cols = st.columns(4)
    for index, cake in enumerate(cakes):
        with cols[index % 4]:
            st.markdown(f"""
                <div class="cake-box">
                    <img src="{cake['image']}" style="width: 100%; border-radius: 15px; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);">
                    <div class="cake-details">
                        <div class="cake-name">{cake['name']}</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            col1, col2 = st.columns(2)
            with col1:
                if st.button("Add to Cart", key=f"add_to_cart_{cake['id']}", use_container_width=True):
                    if st.session_state.user:
                        if 'user_id' in st.session_state.user:
                            add_to_cart(cake['id'])
                        else:
                            st.toast("User ID not found in session state.")
                    else:
                        st.toast("You need to be logged in to add items to the cart", icon="⚠️")
            with col2:
                if st.button("Customize", key=f"customize_{cake['id']}", use_container_width=True):
                    st.session_state.page = "customize"
                    st.session_state.cake_id = cake['id']
                    st.rerun()

            if st.button("View Details", key=f"view_details_{cake['id']}", use_container_width=True):
                st.session_state.page = "cake_details"
                st.session_state.cake_id = cake['id']
                st.rerun()

def add_to_cart(cake_id):
    if not st.session_state.user or 'user_id' not in st.session_state.user:
        st.toast("You need to be logged in to add items to the cart.", icon="⚠️")
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
        st.toast("Failed to add to cart.", icon="❌")

if __name__ == "__main__":
    show()
