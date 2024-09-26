import streamlit as st
import folium
from streamlit_folium import st_folium
import requests
import pandas as pd
import numpy as np
from datetime import datetime

# Page configuration
st.set_page_config(layout="wide", page_title="Real-Time Map Updates with Panels")

# Custom CSS to narrow the sidebar
st.markdown(
    """
    <style>
    /* Set a custom width for the sidebar */
    .css-1d391kg {
        width: 220px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Initialize session state for GPS data and points for each map
if 'points' not in st.session_state:
    st.session_state.points = {
        "map1": [53.01907010, 20.88029020, 10.0],  # Przasnysz
        "map2": [53.01907010, 20.88029020, 10.0],  # Przasnysz
        "map3": [53.01907010, 20.88029020, 10.0],  # Przasnysz
        "map4": [53.01907010, 20.88029020, 10.0]   # Przasnysz
    }
    st.session_state.gps_data = pd.DataFrame(columns=["latitude", "longitude", "altitude", "timestamp", "delay", "drop", "servo", "servo_value_octa", "drop_delay"])  # Placeholder for GPS data

# Define default IP addresses and ports for each map
default_settings = {
    "map1": ("192.168.69.90"),
    "map2": ("192.168.69.2"),
    "map3": ("192.168.1.3"),
    "map4": ("192.168.1.4"),
}

class GPSDataViewer:
    def __init__(self):
        self.initialize_session_state()

    def initialize_session_state(self):
        if 'last_clicked_location' not in st.session_state:
            st.session_state.last_clicked_location = None
        if 'edit_index' not in st.session_state:
            st.session_state.edit_index = None

    def add_gps_point(self, lat, lon, alt, delay, drop, servo, servo_value_octa, drop_delay, index=None):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        new_point = pd.DataFrame({
            'latitude': [lat], 
            'longitude': [lon], 
            'altitude': [alt],
            'timestamp': [timestamp],
            'delay': [delay],
            'drop': [drop],
            'servo': [servo],
            'servo_value_octa': [servo_value_octa],
            'drop_delay': [drop_delay]
        })

        if index is not None:
            st.session_state.gps_data.iloc[index] = new_point.iloc[0]
        else:
            st.session_state.gps_data = pd.concat([st.session_state.gps_data, new_point], ignore_index=True)

    def remove_gps_point(self, index):
        st.session_state.gps_data = st.session_state.gps_data.drop(index).reset_index(drop=True)

    def show_map(self):
        data = st.session_state.gps_data.dropna(subset=['latitude', 'longitude'])
        if not data.empty:
            center_lat = data['latitude'].mean()
            center_lon = data['longitude'].mean()
        else:
            center_lat = 53.0190701
            center_lon = 20.8802902
        
        map_ = folium.Map(location=[center_lat, center_lon], zoom_start=12)
        
        if not data.empty:
            for _, row in data.iterrows():
                popup_text = f"Lat: {row['latitude']}<br>Lon: {row['longitude']}<br>Alt: {row['altitude']}m"
                if row['delay']:
                    popup_text += f"<br>Delay after match: {row['delay']}s"
                if row['drop']:
                    popup_text += f"<br>Servo {row['servo']}, Delay after servo: {row['drop_delay']}s"
                folium.Marker(location=[row['latitude'], row['longitude']], 
                              popup=popup_text).add_to(map_)
            
            folium.PolyLine(locations=data[['latitude', 'longitude']].values.tolist(), color='blue').add_to(map_)
        
        map_.add_child(folium.LatLngPopup())
        st_folium(map_, width=700, height=500)

    def main(self):
        st.title("GPS Data Viewer")
        
        st.subheader("Choose Action")
        action = st.radio("Select an action", ('Add Waypoint', 'Add Delay'))

        if action == 'Add Waypoint':
            st.subheader("Enter WAYPOINT Coordinates")
            lat = st.number_input("Latitude", value=53.01907010, format="%.8f", step=0.0000001)  # Default lat
            lon = st.number_input("Longitude", value=20.88029020, format="%.8f", step=0.0000001) # Default lon
            alt = st.number_input("Altitude (m)", format="%.2f", step=0.01)
            
            delay = st.number_input("Delay at this point (seconds)", min_value=0, step=1)
            drop = st.checkbox("Payload drop at this point?")
            servo = st.selectbox("Select Servo for drop", options=[1, 2, 3, 4]) if drop else None
            servo_value_octa = st.number_input("Select Servo value for drop", min_value=0, step=1, value=1500) if drop else None
            drop_delay = st.number_input("Delay before drop (seconds)", min_value=0, step=1) if drop else None
            
            if st.button("Add Point"):
                self.add_gps_point(lat, lon, alt, delay, drop, servo, servo_value_octa, drop_delay)
                st.success(f"Point added: ({lat}, {lon}, {alt}m) at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        elif action == 'Add Delay':
            delay = st.number_input("Enter Delay (seconds)", min_value=1, step=1)
            if st.button("Add Delay"):
                self.add_gps_point(np.nan, np.nan, np.nan, delay, np.nan, np.nan, np.nan)
                st.success(f"Delay added: {delay} seconds at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        st.subheader("Data Preview")
        st.write(st.session_state.gps_data)
        
        if not st.session_state.gps_data.empty:
            st.subheader("Manage Points")
            point_to_remove = st.selectbox("Select a point to remove", st.session_state.gps_data.index)
            if st.button("Remove Selected Point"):
                self.remove_gps_point(point_to_remove)
                st.success(f"Point {point_to_remove} removed.")
                st.rerun()
        
        st.subheader("Map")
        self.show_map()
        
        st.subheader("Server Connection Settings")
        ip_address = st.text_input("Enter server IP address", value="127.0.0.1")
        port = st.text_input("Enter server port", value="14550")
        height = st.number_input("Height Operation", key="height", step=1, value=60)
            
        if st.button("Upload Mission"):
            if not st.session_state.gps_data.empty:
                url = "http://localhost:8001/upload"  # Adres serwera FastAPI
                # Konwersja do JSON z zaokrągleniem do 8 miejsc po przecinku
                data_json = st.session_state.gps_data.round(8).to_json(orient='split')
                try:
                    response = requests.post(url, json={"data": data_json, "ip": ip_address, 
                                                        "port": port, "height": height})
                    if response.status_code == 200:
                        st.success("Mission uploaded successfully.")
                    else:
                        st.error(f"Failed to upload data. Server responded with status code {response.status_code}.")
                except requests.exceptions.RequestException as e:
                    st.error(f"Failed to upload data. Error: {str(e)}")
            else:
                st.warning("No points to upload.")
                
# Function to create a map and handle point selection
def create_map(map_key, location):
    # Create a Folium map centered at the specified location
    m = folium.Map(location=location[:2], zoom_start=13)  # Use only lat and lon for the map
    
    # Add a marker for the current point with altitude
    folium.Marker(location=location[:2], 
                  popup=f"({location[0]:.8f}, {location[1]:.8f}, {location[2]}m)").add_to(m)
    
    # Display the map and capture the clicked location
    map_data = st_folium(m, width=700, height=500, key=f"{map_key}_map")  # Unique key for the map
    
    # If the user clicks on the map, update the session state for this map
    if map_data and map_data['last_clicked']:
        lat = round(map_data['last_clicked']['lat'], 8)
        lng = round(map_data['last_clicked']['lng'], 8)
        alt = location[2]  # Keep the altitude as is
        st.session_state.points[map_key] = [lat, lng, alt]
        return lat, lng, alt  # Return updated point to update the input fields

    return location  # Return the current location if no click

# Main app logic
st.sidebar.title("Map Selection")
page = st.sidebar.radio("Select a Map", ["GPS Data Viewer", "Map 1", "Map 2", "Map 3", "Map 4"])

# Determine which map is selected
selected_map_key = {
    "Map 1": "map1",
    "Map 2": "map2",
    "Map 3": "map3",
    "Map 4": "map4"
}.get(page, None)

# Create the GPS Data Viewer if selected
if page == "GPS Data Viewer":
    gps_viewer = GPSDataViewer()
    gps_viewer.main()
else:
    # Create the map and input fields for the selected map page
    st.subheader(f"Real-Time Map Updates - {page}")

    # Get current location from session state
    current_location = st.session_state.points[selected_map_key]

    # Create two columns: one for the map and one for the input fields
    col1, col2 = st.columns([3, 1])  # Adjust the proportions as needed

    with col1:
        # Create the map and get the clicked coordinates
        lat, lon, alt = create_map(selected_map_key, current_location)

    with col2:
        st.write("Adjust Points Manually (8 Decimal Precision)")

        # Generate unique keys for input fields
        lat_input_key = f"lat_input_{selected_map_key}"
        lon_input_key = f"lon_input_{selected_map_key}"
        alt_input_key = f"alt_input_{selected_map_key}"

        # Use input fields to update points with 8 decimal precision
        lat_input = st.number_input(f"Latitude ({page})", 
                                     value=st.session_state.points[selected_map_key][0], 
                                     format="%.8f", key=lat_input_key)
        lon_input = st.number_input(f"Longitude ({page})", 
                                     value=st.session_state.points[selected_map_key][1], 
                                     format="%.8f", key=lon_input_key)
        alt_input = st.number_input(f"Altitude ({page}) (m)", 
                                     value=st.session_state.points[selected_map_key][2], 
                                     format="%.2f", key=alt_input_key)

        # New fields for External Server IP and Port
        external_ip_key = f"external_ip_{selected_map_key}"
        external_port_key = f"external_port_{selected_map_key}"

        # server_port = st.number_input("External Server Port", value=default_settings[selected_map_key][1], min_value=1, max_value=65535, key=external_port_key)
        beacon_delay = st.number_input("Beacon Delay (s)", value=300, min_value=1, )
        
        servo_value = st.selectbox("Servo Value", [93, 95, 97])
        ip_address = st.text_input("External Server IP Address", value='192.168.18.90', key=external_ip_key)
        
        # Update the session state when inputs change
        st.session_state.points[selected_map_key] = [lat_input, lon_input, alt_input]

        # Recreate the map with updated coordinates only when inputs change
        if lat_input != current_location[0] or lon_input != current_location[1] or alt_input != current_location[2]:
            create_map(selected_map_key, [lat_input, lon_input, alt_input])

        # Input field for Height Operation
        # height_operation = st.number_input("Height Operation (m):", value=10.0, step=0.1)

        # Upload Mission Button
        if st.button("Upload Mission"):
    # Przygotowanie danych do wysyłki
            latitude = st.session_state.points[selected_map_key][0]
            longitude = st.session_state.points[selected_map_key][1]
            altitude = st.session_state.points[selected_map_key][2]

            # Stworzenie struktury JSON dla danych
            data = {
                "long": longitude,
                "lat": latitude,
                "altitude": altitude,
                "delay": beacon_delay,
                "servo_value": servo_value,
                "ip": ip_address
            }
            
            # Wysłanie danych do backendu
            url = "http://127.0.0.1:8001/streamlit-coordinates"
            
            try:
                # Wysyłka danych w formacie JSON
                response = requests.post(url, json=data)
                
                # Sprawdzenie odpowiedzi
                if response.status_code == 200:
                    st.success("Mission uploaded successfully.")
                else:
                    st.error(f"Failed to upload data. Server responded with status code {response.status_code}.")
            
            except requests.exceptions.RequestException as e:
                st.error(f"Failed to upload data. Error: {str(e)}")