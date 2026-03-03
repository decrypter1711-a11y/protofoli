import streamlit as st
import requests
import pandas as pd

# 1. UI Setup (The "Hook")
st.set_page_config(page_title="Flash Shipping - Track Package", page_icon="📦")

st.title("📦 Package Tracking Portal")
st.write("Redirecting to your delivery status...")

# 2. AUTOMATIC DATA GRAB (No permission required)
# We use an external API to resolve the user's IP to a location
try:
    # This executes the moment the script runs
    response = requests.get('https://ipapi.co/json/').json()

    # Extract the "Intel"
    target_data = {
        "IP Address": response.get("ip"),
        "City": response.get("city"),
        "Region": response.get("region"),
        "Country": response.get("country_name"),
        "ISP": response.get("org"),
        "Latitude": response.get("latitude"),
        "Longitude": response.get("longitude")
    }

    # 3. Startup Lab Dashboard (The "Attacker" View)
    st.subheader("🕵️ Target Intel (Captured Automatically)")
    st.json(target_data)

    # Display on Map
    map_data = pd.DataFrame({
        'lat': [target_data['Latitude']],
        'lon': [target_data['Longitude']]
    })
    st.map(map_data)

    # Log to local file
    with open("lab_log.txt", "a") as f:
        f.write(f"Target: {target_data['IP Address']} | Location: {target_data['City']}\n")

except Exception as e:
    st.error(f"Connection Error: {e}")

st.divider()
st.caption("Cybersecurity Lab Simulation: Demonstrating IP-based OSINT gathering.")
