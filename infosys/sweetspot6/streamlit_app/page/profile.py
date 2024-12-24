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

            .text-box {
                background-color: #ffffff;
                padding: 15px;
                border-radius: 10px;
                margin-bottom: 15px;
                color: #333333;
                box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
                transition: transform 0.3s;
            }
            .text-box:hover {
                transform: scale(1.05);
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

    st.markdown(f"<div style='text-align: left; font-size: 28px; font-weight: bold; color: #FF69B4;'>Your Profile 👉🏽</div>", unsafe_allow_html=True)

    if st.session_state.user:
        user_id = st.session_state.user['user_id']
        response = requests.get(f"http://localhost:8000/api/customers/{user_id}/")

        if response.status_code == 200:
            user = response.json()

            # Create 7 columns
            cols = st.columns(7)

            with cols[3]:
                if user['profile_pic']:
                    st.markdown(
                        f"<img src='{user['profile_pic']}' style='width:120px; height:120px; border-radius:50%; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);'>",
                        unsafe_allow_html=True)
                else:
                    st.markdown(
                        "<img src='https://cdn-icons-png.flaticon.com/512/219/219983.png' style='width:120px; height:120px; border-radius:50%; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);'>",
                        unsafe_allow_html=True)

            col1, col2, col3 = st.columns([1, 2, 1])

            with col2:
                st.markdown(
                    f"<div class='text-box'><strong>Name:</strong> {user['first_name']} {user['last_name']}</div>",
                    unsafe_allow_html=True)
                st.markdown(f"<div class='text-box'><strong>Username:</strong> {user['username']}</div>",
                            unsafe_allow_html=True)
                st.markdown(f"<div class='text-box'><strong>Email:</strong> {user['email']}</div>",
                            unsafe_allow_html=True)
                st.markdown(f"<div class='text-box'><strong>Mobile Number:</strong> {user['mobile_no']}</div>",
                            unsafe_allow_html=True)
                st.markdown(f"<div class='text-box'><strong>Address:</strong> {user['address']}</div>",
                            unsafe_allow_html=True)
                st.markdown(f"<div class='text-box'><strong>City:</strong> {user['city']}</div>",
                            unsafe_allow_html=True)
                st.markdown(f"<div class='text-box'><strong>State:</strong> {user['state']}</div>",
                            unsafe_allow_html=True)
                st.markdown(f"<div class='text-box'><strong>Pincode:</strong> {user['pincode']}</div>",
                            unsafe_allow_html=True)

                if 'image_uploaded' not in st.session_state:
                    st.session_state.image_uploaded = False

                if not st.session_state.image_uploaded:
                    uploaded_file = st.file_uploader("Upload a new profile picture", type=["jpg", "jpeg", "png"])
                    if uploaded_file is not None:
                        files = {'profile_pic': uploaded_file}
                        response = requests.post(f"http://localhost:8000/api/customers/update_profile_picture/",
                                                 files=files, data={'customer_id': user_id})
                        if response.status_code == 200:
                            st.success("Profile picture updated successfully!")
                            st.session_state.image_uploaded = True
                            st.rerun()
                        else:
                            st.error("Failed to update profile picture.")
                else:
                    st.info("Profile picture already uploaded. Refresh the page to upload a new one.")
        else:
            st.error("Failed to fetch user details.")
    else:
        st.error("Please log in to view your profile.")

def __main__():
    show()
