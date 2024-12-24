import streamlit as st
import streamlit.components.v1 as components
import codecs
import requests
import os
import time

def st_slideshow(photoslider_html, height=700):
    current_dir = os.path.dirname(__file__)
    full_path = os.path.join(current_dir, photoslider_html)

    with codecs.open(full_path, 'r', 'utf-8') as slideshow_file:
        page = slideshow_file.read()
    components.html(page, height=height)

# def fetch_notifications():
#     if st.session_state.user:
#         user_id = st.session_state.user['user_id']
#         response = requests.get(f"http://localhost:8000/api/notifications/")
#         if response.status_code == 200:
#             notifications = response.json()
#             for notification in notifications:
#                 st.toast(notification['message'], icon="🔔")
#         else:
#             st.error("Failed to fetch notifications")

def show():
    st.markdown(
        """
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Great+Vibes&family=Poppins:wght@300;400;600&family=Dancing+Script&family=Raleway:wght@400;700&display=swap');
            .stApp {
                background: url('http://localhost:8000/media/banners/bg1.jpg') no-repeat center center fixed; background-size: cover;
                background-size: cover;
                color: #333;
                font-family: 'Poppins', sans-serif;
            }

            .welcome-text {
                text-align: center;
                font-size: 60px;
                font-weight: bold;
                color: #FF6347;
                text-shadow: 4px 4px 8px rgba(0, 0, 0, 0.4);
                margin-top: 20px;
                font-family: 'Great Vibes', cursive;
            }

            .sub-welcome-text {
                text-align: center;
                font-size: 32px;
                color: #D2691E;
                margin-bottom: 40px;
                font-family: 'Dancing Script', cursive;
            }

            .button-container {
                text-align: center;
                margin-top: 40px;
            }

            .custom-button {
                background-color: #FF6347;
                color: white;
                font-size: 24px;
                font-weight: bold;
                padding: 20px 60px;
                border-radius: 30px;
                border: none;
                cursor: pointer;
                transition: background-color 0.3s, transform 0.3s;
                box-shadow: 0 8px 20px rgba(0, 0, 0, 0.4);
                font-family: 'Raleway', sans-serif;
            }

            .custom-button:hover {
                background-color: #FF4500;
                transform: translateY(-8px);
                box-shadow: 0 15px 25px rgba(0, 0, 0, 0.5);
            }

            .logo-container {
                text-align: center;
                margin-top: 20px;
                animation: fadeInLogo 2s ease-in-out;
            }

            .logo-image {
                border-radius: 30px;
                box-shadow: 0 15px 25px rgba(0, 0, 0, 0.4);
                transition: transform 0.4s, box-shadow 0.4s;
            }

            .logo-image:hover {
                transform: scale(1.2);
                box-shadow: 0 20px 30px rgba(0, 0, 0, 0.5);
            }

            .slideshow-container {
                margin-top: 20px;
                margin-bottom: 40px;
                box-shadow: 0 15px 25px rgba(0, 0, 0, 0.3);
                border-radius: 20px;
                overflow: hidden;
            }

            @keyframes fadeInLogo {
                0% { opacity: 0; transform: translateY(-30px); }
                100% { opacity: 1; transform: translateY(0); }
            }
        </style>
        """,
        unsafe_allow_html=True
    )

    _, center_col, _ = st.columns([1, 1, 1])

    with center_col:
        st.markdown(
            """
            <div class='logo-container'>
                <img src='http://localhost:8000/media/profiles/square_logo_dark.png' width='250' class='logo-image'>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("<div class='slideshow-container'>", unsafe_allow_html=True)
    st_slideshow("slider.html")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='welcome-text'>The Dessert Paradise!</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub-welcome-text'>Satisfy your cravings with our heavenly treats!</div>", unsafe_allow_html=True)

    st.markdown("<div class='button-container'>", unsafe_allow_html=True)
    if st.button("Dive into Desserts", use_container_width=False, key='dive_button', help='Click to explore our dessert collection!'):
        st.session_state.page = "cakes"
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

if __name__ == '__main__':
    show()
