import streamlit as st
import pandas as pd
import folium
from folium import plugins
from streamlit_folium import folium_static
from datetime import datetime
import requests

class GPSDataViewer:
    def __init__(self):
        if 'gps_data' not in st.session_state:
            st.session_state.gps_data = pd.DataFrame(columns=['latitude', 'longitude', 'timestamp', 'delay', 'drop', 'servo', 'drop_delay'])
        if 'lat' not in st.session_state:
            st.session_state.lat = 53.0190700
        if 'lon' not in st.session_state:
            st.session_state.lon = 20.8802900
        st.session_state.edit_index=None

    def add_gps_point(self, lat, lon, delay, drop, servo, drop_delay, index=None):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        new_point = pd.DataFrame({
            'latitude': [lat], 
            'longitude': [lon], 
            'timestamp': [timestamp],
            'delay': [delay],
            'drop': [drop],
            'servo': [servo],
            'drop_delay': [drop_delay]
        })

        if index is not None:
            st.session_state.gps_data.iloc[index] = new_point.iloc[0]
        else:
            st.session_state.gps_data = pd.concat([st.session_state.gps_data, new_point], ignore_index=True)

        return st.session_state.gps_data

    def remove_gps_point(self, index):
        st.session_state.gps_data = st.session_state.gps_data.drop(index).reset_index(drop=True)
        return st.session_state.gps_data

    def show_map(self):
        data = st.session_state.gps_data
        if not data.empty:
            center_lat = data['latitude'].mean()
            center_lon = data['longitude'].mean()
            map_ = folium.Map(location=[center_lat, center_lon], zoom_start=12)
            
            for _, row in data.iterrows():
                popup_text = f"Time: {row['timestamp']}"
                if row['delay']:
                    popup_text += f"<br>Delay: {row['delay']}s"
                if row['drop']:
                    popup_text += f"<br>Drop: Servo {row['servo']}, Delay: {row['drop_delay']}s"
                folium.Marker(location=[row['latitude'], row['longitude']], 
                              popup=popup_text).add_to(map_)
            
            folium.PolyLine(locations=data[['latitude', 'longitude']].values.tolist(), color='blue').add_to(map_)
            
            sw = data[['latitude', 'longitude']].min().values.tolist()
            ne = data[['latitude', 'longitude']].max().values.tolist()
            map_.fit_bounds([sw, ne])
            
            folium_static(map_)
        else:
            st.warning("No GPS data available to display.")

    def main(self):
        st.title("GPS Data Viewer")
        
        st.subheader("Enter GPS Coordinates")
        lat = st.number_input("Latitude", format="%.6f", value=st.session_state.lat, key="lat_input")
        lon = st.number_input("Longitude", format="%.6f", value=st.session_state.lon, key="lon_input")
        
        delay = st.number_input("Delay at this point (seconds)", min_value=0, step=1)
        drop = st.checkbox("Payload drop at this point?")
        servo = st.selectbox("Select Servo for drop", options=[1, 2, 3, 4]) if drop else None
        drop_delay = st.number_input("Delay before drop (seconds)", min_value=0, step=1) if drop else None
        
        if st.button("Add Point"):
            if st.session_state.edit_index is not None:
                self.add_gps_point(lat, lon, delay, drop, servo, drop_delay, index=st.session_state.edit_index)
                st.success(f"Point {st.session_state.edit_index} updated.")
                st.session_state.edit_index = None
            else:
                if len(st.session_state.gps_data) < 15:
                    self.add_gps_point(lat, lon, delay, drop, servo, drop_delay)
                    st.success(f"Point added: ({lat}, {lon}) at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                    st.session_state.lat = 53.0190700
                    st.session_state.lon = 20.8802900
                else:
                    st.warning("You can add up to 15 points only.")
        
        st.subheader("Data Preview")
        st.write(st.session_state.gps_data)
        
        if not st.session_state.gps_data.empty:
            st.subheader("Manage Points")
            point_to_remove = st.selectbox("Select a point to remove", st.session_state.gps_data.index)
            if st.button("Remove Selected Point"):
                self.remove_gps_point(point_to_remove)
                st.success(f"Point {point_to_remove} removed.")
                st.rerun()
            
            if st.button("Remove All Points"):
                st.session_state.gps_data = pd.DataFrame(columns=['latitude', 'longitude', 'timestamp', 'delay', 'drop', 'servo', 'drop_delay'])
                st.success("All points removed.")
                st.rerun()
        
        if st.button("Upload Mission"):
            if not st.session_state.gps_data.empty:
                url = "http://localhost:8001/upload"  # Adres serwera FastAPI
                data_json = st.session_state.gps_data.to_json(orient='split')
                try:
                    response = requests.post(url, json={"data": data_json})
                    if response.status_code == 200:
                        st.success("Mission uploaded successfully.")
                    else:
                        st.error(f"Failed to upload data. Server responded with status code {response.status_code}.")
                except requests.exceptions.RequestException as e:
                    st.error(f"Failed to upload data. Error: {str(e)}")
            else:
                st.warning("No points to upload.")

        st.subheader("Map")
        self.show_map()

# To use the class:
viewer = GPSDataViewer()
viewer.main()
