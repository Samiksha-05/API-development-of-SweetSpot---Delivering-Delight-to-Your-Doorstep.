import streamlit as st

st.set_page_config(page_title="SweetSpot", layout="wide")

from components.sidebar import sidebar
from page import home, cakes, cart, auth, profile, cake_details, customize, checkout, store, store_cakes

base_url = "http://localhost:8000"

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Lato:wght@400;700&display=swap');

    body {
        font-family: 'Lato', sans-serif;
        background-color: #1E1E1E;
        color: #FFFFFF;
    }

    .stTabs {
        background-color: #1E1E1E;
        padding: 10px 10px 30px;
        border-radius: 15px;
        margin-bottom: 30px;
    }

    .stTabs [data-baseweb="tab-list"] {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        justify-content: center;
        padding: 7px;
    }

    .stTabs [data-baseweb="tab"] {
        flex-grow: 0;
        flex-shrink: 0;
        flex-basis: auto;
        height: auto;
        white-space: normal;
        border-radius: 5px;
        color: #FFFFFF;
        background-color: #2C2C2C;
        border: 1px solid #3A3A3A;
        padding: 10px 15px;
        font-size: 16px;
        font-weight: bold;
        transition: all 0.3s ease;
        text-align: center;
        min-width: 100px;
    }

    .stTabs [data-baseweb="tab"]:hover {
        background-color: #3A3A3A;
    }

    .stTabs [aria-selected="true"] {
        background-color: #4A4A4A;
        color: #FFFFFF;
        border: 1px solid #5A5A5A;
    }

    .stTextInput > div > div > input {
        background-color: #2C2C2C;
        color: #FFFFFF;
    }

    .stForm {
        background-color: #1E1E1E;
        padding: 20px;
        border-radius: 10px;
    }

    .stForm > div {
        margin-bottom: 20px;
    }

    /* Updated button styles */
    .stButton > button,
    .stForm [data-testid="stFormSubmitButton"] > button {
        color: white;
        border: none;
        padding: 10px 24px;
        font-size: 12px;
        border-radius: 5px;
        border: 1px solid #2C2C2C;
        transition: all 0.3s ease;
        font-weight: bold;
        text-transform: uppercase;
        letter-spacing: 1px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        width: 100%;
        margin-top: 10px;
        cursor: pointer;
        background-color: #4c3451;  /* Before click color */
    }

    .stButton > button:hover,
    .stForm [data-testid="stFormSubmitButton"] > button:hover {
        background-color: #5a3d6b;  /* Hover color */
        box-shadow: 0 6px 8px rgba(0, 0, 0, 0.15);
    }

    .stButton > button:active,
    .stForm [data-testid="stFormSubmitButton"] > button:active {
        background-color: #762586;  /* After click color */
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        transform: translateY(2px);
    }

    /* Ensure text is always visible */
    .stButton > button > div,
    .stForm [data-testid="stFormSubmitButton"] > button > div {
        color: white !important;
    }

    .success-message {
        background-color: #4CAF50;
        color: white;
        padding: 10px;
        border-radius: 5px;
        margin-top: 10px;
        text-align: center;
        animation: fadeIn 0.5s;
    }

    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }

    .profile-pic {
        width: 50px;
        height: 50px;
        border-radius: 50%;
        object-fit: cover;
        margin-bottom: 10px;
    }

    /* Sidebar styling */
    .profile-pic {
        width: 50px;
        height: 50px;
        border-radius: 50%;
        object-fit: cover;
        margin-bottom: 10px;
    }

    /* Sidebar styling */
    .sidebar .sidebar-content {
        background-color: #2C2C2C;
    }

    /* Button styling */
    .sidebar .stButton > button {
    width: 100%;
    margin-bottom: 10px;
    color: white;
    border: none;
    padding: 10px 15px;
    font-size: 16px;  /* Default font size */
    border-radius: 5px;
    cursor: pointer;
    transition: background-color 0.3s ease;
    }

    .sidebar .stButton > button p {
        font-size: 12px;  /* Adjusted font size */
        margin: 0;  /* Remove default margin */
    }

    .sidebar .stButton > button:hover {
        background-color: #FF6B6B;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'user' not in st.session_state:
    st.session_state.user = None

if 'page' not in st.session_state:
    st.session_state.page = "home"

if 'cake_id' not in st.session_state:
    st.session_state.cake_id = None

def main():
    pages = {
        "home": home.show,
        "cakes": cakes.show,
        "cart": cart.show,
        "profile": profile.show,
        "auth": auth.show,
        "cake_details": lambda: cake_details.show(st.session_state.cake_id),
        "customize": customize.show,
        "checkout": lambda: checkout.show(st.session_state.order_id),
        "store": store.show,
        "store_cakes": store_cakes.show
    }

    if st.session_state.page in pages:
        pages[st.session_state.page]()
    else:
        st.error("Page not found")


# Run the app
if __name__ == "__main__":
    sidebar()
    main()