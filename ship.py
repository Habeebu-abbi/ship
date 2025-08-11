import streamlit as st
import pandas as pd
import folium
from streamlit_folium import folium_static
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import time

# Function to geocode postal codes
def geocode_postal_code(postal_code, country='India'):
    geolocator = Nominatim(user_agent="postal_code_locator")
    location = None
    retries = 3
    
    while retries > 0:
        try:
            location = geolocator.geocode(f"{postal_code}, {country}")
            break
        except:
            retries -= 1
            time.sleep(1)
    
    if location:
        return (location.latitude, location.longitude)
    return None

# Load data
@st.cache_data
def load_data():
    # Sample data - replace with your actual data loading
    hubs_data = {
        'Delivery Hub': [
            'Hebbal [ BH Micro warehouse ]',
            'Banashankari [ BH Micro warehouse ]',
            'Mahadevapura [ BH Micro warehouse ]',
            'Chandra Layout [ BH Micro warehouse ]',
            'Kudlu [ BH Micro warehouse ]',
            'Koramangala NGV [ BH Micro warehouse ]',
            'Domlur [ BH Micro warehouse ]'
        ],
        'Lat': [
            13.066819, 12.89162, 12.9908333, 12.997615, 
            12.8798786, 12.88021201, 12.96085507
        ],
        'Long': [
            77.604538, 77.55644, 77.7042778, 77.5138312, 
            77.6529101, 77.65505249, 77.63714234
        ]
    }
    
    postal_data = {
        'Delivery Hub': [
            'Banashankari [ BH Micro warehouse ]',
            'Banashankari [ BH Micro warehouse ]',
            'Banashankari [ BH Micro warehouse ]',
            'Banashankari [ BH Micro warehouse ]',
            'Banashankari [ BH Micro warehouse ]',
            'Banashankari [ BH Micro warehouse ]',
            'Banashankari [ BH Micro warehouse ]',
            'Banashankari [ BH Micro warehouse ]',
            'Banashankari [ BH Micro warehouse ]',
            'Hebbal [ BH Micro warehouse ]',
            'Hebbal [ BH Micro warehouse ]',
            'Hebbal [ BH Micro warehouse ]',
            'Mahadevapura [ BH Micro warehouse ]',
            'Mahadevapura [ BH Micro warehouse ]',
            'Domlur [ BH Micro warehouse ]'
        ],
        'Shipping Postal Code': [
            '560004', '560011', '560018', '560019', '560028',
            '560029', '560041', '560050', '560061', '560024',
            '560032', '560077', '560048', '560068', '560071'
        ]
    }
    
    hubs_df = pd.DataFrame(hubs_data)
    postal_df = pd.DataFrame(postal_data)
    
    return hubs_df, postal_df

def calculate_distances(hub_coords, postal_df_with_coords):
    distances = []
    for _, row in postal_df_with_coords.iterrows():
        if row['Coordinates']:
            dist = geodesic(hub_coords, row['Coordinates']).km
            distances.append(round(dist, 2))
        else:
            distances.append(None)
    return distances

def main():
    st.title("Delivery Hub and Postal Code Mapping")
    
    # Load data
    hubs_df, postal_df = load_data()
    
    # File uploader
    uploaded_file = st.file_uploader("Upload your CSV file with Delivery Hub and Postal Codes", type=["csv"])
    
    if uploaded_file is not None:
        try:
            postal_df = pd.read_csv(uploaded_file)
            st.success("File uploaded successfully!")
        except Exception as e:
            st.error(f"Error reading file: {e}")
    
    # Geocode postal codes
    with st.spinner('Geocoding postal codes... This may take a while'):
        postal_df['Coordinates'] = postal_df['Shipping Postal Code'].apply(geocode_postal_code)
    
    # Filter out None values (failed geocoding)
    valid_postal_df = postal_df.dropna(subset=['Coordinates'])
    
    # Hub selection
    st.sidebar.header("Filter Options")
    selected_hub = st.sidebar.selectbox(
        "Select a Delivery Hub",
        hubs_df['Delivery Hub'].unique(),
        index=0
    )
    
    # Get selected hub coordinates
    selected_hub_row = hubs_df[hubs_df['Delivery Hub'] == selected_hub].iloc[0]
    hub_coords = (selected_hub_row['Lat'], selected_hub_row['Long'])
    
    # Filter postal codes for selected hub
    hub_postal_df = valid_postal_df[valid_postal_df['Delivery Hub'] == selected_hub].copy()
    
    # Calculate distances
    hub_postal_df['Distance (km)'] = calculate_distances(hub_coords, hub_postal_df)
    
    # Sort by distance
    hub_postal_df = hub_postal_df.sort_values('Distance (km)')
    
    # Display filtered data
    st.subheader(f"Postal Codes Served by {selected_hub}")
    st.dataframe(hub_postal_df[['Shipping Postal Code', 'Distance (km)']])
    
    # Create map centered on selected hub
    m = folium.Map(location=[selected_hub_row['Lat'], selected_hub_row['Long']], zoom_start=12)
    
    # Add selected hub to the map
    folium.Marker(
        location=[selected_hub_row['Lat'], selected_hub_row['Long']],
        popup=selected_hub,
        icon=folium.Icon(color='blue', icon='warehouse', prefix='fa')
    ).add_to(m)
    
    # Add circle around the hub
    folium.Circle(
        location=[selected_hub_row['Lat'], selected_hub_row['Long']],
        radius=3000,  # 3km radius
        color='blue',
        fill=True,
        fill_color='blue',
        fill_opacity=0.2,
        popup=f"{selected_hub} Coverage Area"
    ).add_to(m)
    
    # Add postal codes to the map with distance-based coloring
    for idx, row in hub_postal_df.iterrows():
        lat, long = row['Coordinates']
        postal_code = row['Shipping Postal Code']
        distance = row['Distance (km)']
        
        # Color based on distance (green = close, orange = medium, red = far)
        if distance < 3:
            color = 'green'
        elif distance < 6:
            color = 'orange'
        else:
            color = 'red'
        
        # Add marker for postal code
        folium.Marker(
            location=[lat, long],
            popup=f"Postal Code: {postal_code}\nDistance: {distance} km",
            icon=folium.Icon(color=color, icon='envelope', prefix='fa')
        ).add_to(m)
        
        # Add line from hub to postal code
        folium.PolyLine(
            locations=[hub_coords, [lat, long]],
            color='gray',
            weight=1,
            dash_array='5,5'
        ).add_to(m)
    
    # Display the map
    folium_static(m)
    
    # Distance distribution chart
    st.subheader("Distance Distribution")
    st.bar_chart(hub_postal_df.set_index('Shipping Postal Code')['Distance (km)'])
    
    # Show statistics
    st.subheader("Coverage Statistics")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Postal Codes", len(hub_postal_df))
    
    with col2:
        avg_dist = hub_postal_df['Distance (km)'].mean()
        st.metric("Average Distance (km)", round(avg_dist, 2))
    
    with col3:
        furthest = hub_postal_df['Distance (km)'].max()
        st.metric("Furthest Postal Code (km)", furthest)

if __name__ == "__main__":
    main()