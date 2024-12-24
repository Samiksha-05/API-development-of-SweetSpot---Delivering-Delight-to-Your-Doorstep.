import streamlit as st
import requests

def fetch_stores():
    response = requests.get("http://localhost:8000/api/stores/")
    if response.status_code == 200:
        return response.json()
    else:
        st.error("Failed to fetch stores")
        return []

def fetch_cakes(store_id):
    response = requests.get(f"http://localhost:8000/api/stores/{store_id}/cakes/")
    if response.status_code == 200:
        return response.json()
    else:
        st.error("Failed to fetch cakes")
        return []

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

            .store-image {
                border: 2px solid #800080;
                border-radius: 15px;
                width: 120px;
                height: 120px;
                display: block;
                margin: auto;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
            }
            .store-details {
                background-color: #ffffff;
                padding: 20px;
                border-radius: 15px;
                box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
                margin-bottom: 20px;
                color: #333333;
                transition: transform 0.3s;
            }
            .store-details:hover {
                transform: scale(1.05);
            }
            .store-name {
                font-size: 22px;
                font-weight: bold;
                color: #FF69B4;
                margin-bottom: 8px;
            }
            .store-address {
                font-size: 16px;
                color: #666666;
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

    stores = fetch_stores()

    st.markdown("""
        <div style='text-align: center; font-size: 28px; font-weight: bold; color: #FF69B4;'>
            🎂 Cakes to Your Door: Find Stores 🏪
        </div>
    """, unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    for store in stores:
        col1, col2, col3 = st.columns([1, 4, 1])
        with col1:
            st.markdown(f"""
                <div class="store-image">
                    <img src="{store['store_image']}" style="width: 100%; height: 100%; border-radius: 15px;">
                </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
                <div class="store-details">
                    <div class="store-name">{store['name']}</div>
                    <div class="store-address">{store['address']}, {store['city']} - Contact: {store['contact_number']}</div>
                </div>
            """, unsafe_allow_html=True)

        with col3:
            if st.button("Cake Collection", key=store["id"]):
                st.session_state.selected_store = store["id"]
                st.session_state.selected_store_name = store["name"]
                st.session_state.page = "store_cakes"
                st.rerun()

if __name__ == "__main__":
    show()
