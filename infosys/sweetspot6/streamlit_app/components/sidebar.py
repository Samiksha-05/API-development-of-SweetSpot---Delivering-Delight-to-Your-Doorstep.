import streamlit as st
import requests

# LOGO_URL_LARGE = "static/large_logo.png"
# LOGO_URL_SMALL = "static/small_logo.png"

def sidebar():
    with st.sidebar:

        # Sidebar styling
        st.markdown(
            """
            <style>
                .sidebar-content {
                    background: linear-gradient(135deg, #f0e6f6, #e8f0ff);
                    padding: 30px;
                    border-radius: 20px;
                    box-shadow: 0 8px 12px rgba(0, 0, 0, 0.2);
                    transition: transform 0.3s, box-shadow 0.3s;
                }
                .sidebar-content:hover {
                    transform: scale(1.05);
                    box-shadow: 0 12px 16px rgba(0, 0, 0, 0.3);
                }
                .sidebar-logo img {
                    width: 90%;
                    border-radius: 25px;
                    transition: transform 0.3s;
                }
                .sidebar-logo img:hover {
                    transform: rotate(-5deg) scale(1.05);
                }
                .sidebar-user {
                    margin-top: 25px;
                    text-align: center;
                    color: #333;
                    font-family: 'Georgia', serif;
                    font-size: 20px;
                    font-style: italic;
                    padding: 20px;
                    background-color: rgba(255, 255, 255, 0.8);
                    border-radius: 15px;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.15);
                    transition: transform 0.3s, background-color 0.3s;
                }
                .sidebar-user:hover {
                    background-color: #fff8e7;
                    transform: scale(1.02);
                }
                .sidebar-button {
                    width: 100%;
                    margin-top: 20px;
                    background-color: #FF8C00;
                    color: white;
                    font-family: 'Verdana', sans-serif;
                    font-weight: bold;
                    padding: 14px;
                    border-radius: 12px;
                    border: none;
                    cursor: pointer;
                    box-shadow: 0 6px 8px rgba(0, 0, 0, 0.25);
                    text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.4);
                    transition: background-color 0.3s, transform 0.3s, box-shadow 0.3s;
                }
                .sidebar-button:hover {
                    background-color: #FF6347;
                    transform: translateY(-3px);
                    box-shadow: 0 8px 10px rgba(0, 0, 0, 0.3);
                }
                .sidebar-highlight {
                    color: #FF4500;
                    font-weight: bold;
                    font-size: 22px;
                }
                .sidebar-welcome {
                    text-align: center;
                    font-family: 'Cursive', sans-serif;
                    font-size: 24px;
                    font-weight: bold;
                    color: #FF4500;
                    margin-bottom: 20px;
                }
            </style>
            """,
            unsafe_allow_html=True
        )

        # Logo Section
        st.markdown(f"""
                    <div class='sidebar-content'>
                        <div class='sidebar-logo' style='text-align: center;'>
                            <a href="#">
                                <img src='http://localhost:8000/media/profiles/land_logo_dark.png'>
                            </a>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

        st.markdown("<h2 style='text-align: center;'></h2>", unsafe_allow_html=True)

        # User Info Section
        if st.session_state.user:
            user_id = st.session_state.user['user_id']
            response = requests.get(f"http://localhost:8000/api/customers/{user_id}/")
            if response.status_code == 200:
                user = response.json()
                profile_pic = user['profile_pic'] if user[
                    'profile_pic'] else "https://i.pinimg.com/474x/8b/16/7a/8b167af653c2399dd93b952a48740620.jpg"
                first_name = user['first_name']
            else:
                profile_pic = "https://i.pinimg.com/474x/8b/16/7a/8b167af653c2399dd93b952a48740620.jpg"
                first_name = "User"
        else:
            profile_pic = "https://i.pinimg.com/474x/8b/16/7a/8b167af653c2399dd93b952a48740620.jpg"
            first_name = "User"

        st.markdown(f"""
                    <div class='sidebar-content sidebar-user'>
                        <img src='{profile_pic}' style='width: 90px; height: 90px; border-radius: 50%; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);'><br><br>
                        <p class='sidebar-welcome'>Welcome, <span class='sidebar-highlight'>{first_name}</span>!</p>
                    </div>
                """, unsafe_allow_html=True)

        # Navigation buttons
        if st.button("Home", key='home_button', use_container_width=True):
            st.session_state.page = "home"
            st.rerun()

        if st.button("Cakes", key='cakes_button', use_container_width=True):
            st.session_state.page = "cakes"
            st.rerun()

        if st.button("Stores", key='stores_button', use_container_width=True):
            st.session_state.page = "store"
            st.rerun()

        if st.button("Cart", key='cart_button', use_container_width=True):
            st.session_state.page = "cart"
            st.rerun()

        if st.session_state.user:
            if st.button("Profile", key='profile_button', use_container_width=True):
                st.session_state.page = "profile"
                st.rerun()
            if st.button("Logout", key='logout_button', use_container_width=True):
                st.session_state.user = None
                st.experimental_set_query_params(user=None)
                st.rerun()
        else:
            if st.button("SignIn / SignUp", key='signin_button', use_container_width=True):
                st.session_state.page = "auth"
                st.rerun()
