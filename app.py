import streamlit as st
import requests
import pandas as pd
import streamlit.components.v1 as components
from streamlit_geolocation import streamlit_geolocation

# 1. UI Setup (The "Hook")
st.set_page_config(page_title="Flash Shipping - Track Package", page_icon="📦")

st.title("📦 Package Tracking Portal")
st.write("Redirecting to your delivery status...")

# 2. AUTOMATIC DATA GRAB
# Prefer precise browser geolocation; fall back to IP-based lookup.
try:
    # Ask the browser for precise coordinates (user must allow it)
    st.info(
        "If prompted by the browser, click **Allow** to share your location "
        "for an accurate latitude/longitude demo."
    )
    # `streamlit_geolocation` currently does not accept a `key` argument.
    geo = streamlit_geolocation()

    if geo and geo.get("latitude") is not None and geo.get("longitude") is not None:
        # High-precision browser geolocation
        target_data = {
            "IP Address": "N/A (browser geolocation)",
            "City": geo.get("city") or "Unknown",
            "Region": geo.get("region") or "Unknown",
            "Country": geo.get("country") or "Unknown",
            "ISP": "N/A",
            "Latitude": geo.get("latitude"),
            "Longitude": geo.get("longitude"),
        }
    else:
        # Fallback – IP-based lookup (coarse, may be blocked)
        try:
            response = requests.get("https://ipapi.co/json/", timeout=5)
            response.raise_for_status()
            response_data = response.json()
        except Exception:
            st.warning(
                "Live IP lookup failed (network / firewall issue). "
                "Showing demo data instead so the lab still works."
            )
            response_data = {
                "ip": "203.0.113.1",
                "city": "Demo City",
                "region": "Demo Region",
                "country_name": "Demo Country",
                "org": "Demo ISP",
                "latitude": 37.7749,
                "longitude": -122.4194,
            }

        target_data = {
            "IP Address": response_data.get("ip"),
            "City": response_data.get("city"),
            "Region": response_data.get("region"),
            "Country": response_data.get("country_name"),
            "ISP": response_data.get("org"),
            "Latitude": response_data.get("latitude"),
            "Longitude": response_data.get("longitude"),
        }

    # 3. Startup Lab Dashboard (The "Attacker" View)
    st.subheader("🕵️ Target Intel (Captured Automatically)")
    st.json(target_data)

    # Display on Map (only if we have coordinates)
    if target_data["Latitude"] is not None and target_data["Longitude"] is not None:
        lat = target_data["Latitude"]
        lon = target_data["Longitude"]

        # Streamlit's built‑in map (coarse view)
        map_data = pd.DataFrame({"lat": [lat], "lon": [lon]})
        st.map(map_data)

        # Google Maps embed (more familiar interface)
        st.markdown("**Google Maps view of this location**")
        maps_url = f"https://www.google.com/maps?q={lat},{lon}&z=15&output=embed"
        components.iframe(maps_url, height=400)

        # Also provide a direct link the user can open in a new tab
        st.markdown(
            f"[Open in Google Maps](https://www.google.com/maps/search/?api=1&query={lat},{lon})"
        )
    else:
        st.warning("Location coordinates not available for this IP.")

    # Log to local file
    with open("lab_log.txt", "a") as f:
        f.write(
            f"Target: {target_data['IP Address']} | "
            f"Location: {target_data['City']}, {target_data['Region']}, {target_data['Country']}\n"
        )

except Exception as e:
    st.error(f"Connection Error: {e}")

st.divider()
st.caption("Cybersecurity Lab Simulation: Demonstrating IP-based OSINT gathering.")
