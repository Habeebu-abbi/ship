import streamlit as st
import pandas as pd
import math
import folium
from streamlit_folium import folium_static
from geopy.distance import geodesic  # For more accurate distance calculations (optional)

# ------------------------------------
# Utility: Haversine Distance Function
# ------------------------------------
def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Earth radius in kilometers
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

# ------------------------------------
# Hub Data
# ------------------------------------
delivery_hubs = [
    {"hub": "Hebbal [ BH Micro warehouse ]", "lat": 13.066819, "lon": 77.604538, "pincodes": [
        560005,560006,560024,560032,560033,560037,560043,560045,560054,560063,560064,560065,
        560077,560080,560084,560092,560094,560097,560106,560113,562123
    ]},
    {"hub": "Banashankari [ BH Micro warehouse ]", "lat": 12.891627, "lon": 77.55644, "pincodes": [
        560004,560011,560018,560019,560028,560029,560041,560050,560061,560062,560069,560070,
        560076,560078,560082,560083,560085,560108,560109,560111
    ]},
    {"hub": "Mahadevapura [ BH Micro warehouse ]", "lat": 12.9908333, "lon": 77.7042778, "pincodes": [
        560016,560036,560037,560043,560048,560049,560066,560067,560087,560093
    ]},
    {"hub": "Chandra Layout [ BH Micro warehouse ]", "lat": 12.997615, "lon": 77.5138312, "pincodes": [
        560002,560003,560009,560010,560012,560013,560014,560015,560020,560021,560022,560023,
        560026,560039,560040,560044,560053,560055,560056,560058,560059,560060,
        560072,560073,560079,560086,560090,560091,560096,560098,560104,560107,560110,562130
    ]},
    {"hub": "Kudlu [ BH Micro warehouse ]", "lat": 12.8798786, "lon": 77.6529101, "pincodes": [
        560001,560007,560008,560017,560025,560027,560030,560034,560035,560038,560042,560046,
        560047,560051,560052,560068,560071,560075,560081,560095,560099,560100,560102,560103,560114
    ]},
    {"hub": "Domlur [ BH Micro warehouse ]", "lat": 12.96085507, "lon": 77.63714234, "pincodes": [
560001, 560007, 560008, 560017, 560025, 560027, 560030, 560031, 560034, 560038, 560042, 560046, 560047, 560051, 560052, 560071, 560075, 560095 
    ]}
]

# ------------------------------------
# Pincode coordinates
# ------------------------------------
pincode_coords = {
    560001: (12.9756, 77.6047),
    560002: (12.9644, 77.5800),
    560003: (12.9911, 77.5850),
    560004: (12.9604, 77.5840),
    560005: (12.9948, 77.6067),
    560006: (12.9985, 77.6175),
    560007: (12.9989, 77.6260),
    560008: (12.9783, 77.6400),
    560009: (12.9731, 77.5880),
    560010: (12.9802, 77.5608),
    560011: (12.9334, 77.5644),
    560012: (13.0055, 77.5653),
    560013: (13.0153, 77.5650),
    560014: (13.0214, 77.5951),
    560015: (13.0160, 77.6076),
    560016: (12.9860, 77.6790),
    560017: (12.9719, 77.6410),
    560018: (12.9260, 77.5560),
    560019: (12.9030, 77.5588),
    560020: (12.9984, 77.5600),
    560021: (13.0025, 77.5565),
    560022: (12.9990, 77.5505),
    560023: (13.0055, 77.5465),
    560024: (13.0235, 77.6195),
    560025: (12.9714, 77.6210),
    560026: (12.9874, 77.5740),
    560027: (12.9490, 77.6250),
    560028: (12.9300, 77.5808),
    560029: (12.9348, 77.6161),
    560030: (12.9434, 77.6205),
    560031: (12.9580, 77.6372),
    560032: (13.0284, 77.6394),
    560033: (13.0420, 77.6205),
    560034: (12.9355, 77.6222),
    560035: (12.9120, 77.6330),
    560036: (12.9910, 77.7022),
    560037: (12.9821, 77.6958),
    560038: (12.9625, 77.6382),
    560039: (12.9763, 77.5580),
    560040: (12.9700, 77.5408),
    560041: (12.9200, 77.6100),
    560042: (12.9745, 77.6555),
    560043: (13.0232, 77.6660),
    560044: (12.9630, 77.5338),
    560045: (13.0298, 77.6414),
    560046: (12.9842, 77.6590),
    560047: (12.9986, 77.6508),
    560048: (12.9840, 77.7130),
    560049: (13.0228, 77.7080),
    560050: (12.9461, 77.5755),
    560051: (12.9692, 77.6565),
    560052: (12.9613, 77.6485),
    560053: (12.9720, 77.5298),
    560054: (13.0498, 77.5905),
    560055: (12.9768, 77.5222),
    560056: (12.9915, 77.5170),
    560057: (13.0091, 77.5072),
    560058: (13.0155, 77.4940),
    560059: (12.9983, 77.5005),
    560060: (12.9530, 77.5038),
    560061: (12.8805, 77.5655),
    560062: (12.8580, 77.5730),
    560063: (13.0530, 77.6240),
    560064: (13.0770, 77.6285),
    560065: (13.0668, 77.6400),
    560066: (12.9848, 77.7450),
    560067: (13.0504, 77.7200),
    560068: (12.9060, 77.6475),
    560069: (12.9005, 77.5600),
    560070: (12.9090, 77.5655),
    560071: (12.9050, 77.6600),
    560072: (12.9717, 77.5132),
    560073: (12.9790, 77.5270),
    560075: (12.8905, 77.5965),
    560076: (12.9050, 77.6034),
    560077: (13.0350, 77.6508),
    560078: (12.9076, 77.5810),
    560079: (13.0148, 77.5430),
    560080: (13.0510, 77.5800),
    560081: (12.8972, 77.6528),
    560082: (12.9308, 77.5908),
    560083: (12.9245, 77.5750),
    560084: (13.0400, 77.6030),
    560085: (12.9115, 77.5770),
    560086: (12.9890, 77.5278),
    560087: (12.9209, 77.7345),
    560090: (13.0110, 77.5320),
    560091: (12.9940, 77.5342),
    560092: (13.0390, 77.5870),
    560093: (12.9650, 77.7150),
    560094: (13.0460, 77.6020),
    560095: (12.9300, 77.6420),
    560096: (12.9760, 77.5160),
    560097: (13.0545, 77.5995),
    560098: (12.9885, 77.5295),
    560099: (12.8895, 77.6430),
    560100: (12.8950, 77.6780),
    560102: (12.8997, 77.6777),
    560103: (12.9125, 77.6590),
    560104: (12.9820, 77.5150),
    560106: (13.0600, 77.6230),
    560107: (12.9860, 77.5205),
    560108: (12.9194, 77.5808),
    560109: (12.9100, 77.5785),
    560110: (12.9770, 77.5135),
    560111: (12.9055, 77.5620),
    560113: (13.0655, 77.5952),
    560114: (12.8770, 77.6445),
    562123: (13.1560, 77.6510),
    562130: (13.0425, 77.4855)
}

# ------------------------------------
# Streamlit App
# ------------------------------------
st.title("📍 Delivery Hub to Postal Code Distance Dashboard")
st.write("Shows nearest postal codes for each delivery hub, with distances and route maps.")

# First show all hubs with their pincodes
for hub in delivery_hubs:
    st.subheader(f"{hub['hub']}")

    rows = []
    for pincode in hub["pincodes"]:
        if pincode in pincode_coords:
            pc_lat, pc_lon = pincode_coords[pincode]
            distance_km = haversine(hub["lat"], hub["lon"], pc_lat, pc_lon)
            rows.append({
                "Pincode": pincode,
                "Latitude": pc_lat,
                "Longitude": pc_lon,
                "Distance_km": round(distance_km, 2)
            })

    if rows:
        df = pd.DataFrame(rows).sort_values(by="Distance_km")
        st.dataframe(df)

        # Map with route lines
        m = folium.Map(location=[hub["lat"], hub["lon"]], zoom_start=12)
        
        # Add hub marker
        folium.Marker(
            [hub["lat"], hub["lon"]],
            popup=f"<b>{hub['hub']}</b>",
            icon=folium.Icon(color="red", icon="warehouse")
        ).add_to(m)
        
        # Add pincode markers and routes
        for _, row in df.iterrows():
            folium.Marker(
                [row["Latitude"], row["Longitude"]],
                popup=f"Pincode: {row['Pincode']}",
                icon=folium.Icon(color="blue", icon="map-pin")
            ).add_to(m)
            
            # Draw a line between hub and pincode
            folium.PolyLine(
                locations=[
                    [hub["lat"], hub["lon"]],
                    [row["Latitude"], row["Longitude"]]
                ],
                color="green",
                weight=2,
                opacity=0.7
            ).add_to(m)
        
        folium_static(m)
    else:
        st.warning("No coordinates found for the postal codes of this hub yet.")

# ------------------------------------
# Mismatch Analysis Section
# ------------------------------------
st.title("🔍 Pincode-Hub Mismatch Analysis")
st.write("Identifying pincodes that might be better served by a different hub")

mismatches = []

for hub in delivery_hubs:
    for pincode in hub["pincodes"]:
        if pincode in pincode_coords:
            pc_lat, pc_lon = pincode_coords[pincode]
            
            # Calculate distance to all hubs
            distances = []
            for other_hub in delivery_hubs:
                dist = haversine(pc_lat, pc_lon, other_hub["lat"], other_hub["lon"])
                distances.append({
                    "Current Hub": hub["hub"],
                    "Pincode": pincode,
                    "Hub": other_hub["hub"],
                    "Distance (km)": round(dist, 2)
                })
            
            # Find the closest hub
            closest_hub = min(distances, key=lambda x: x["Distance (km)"])
            
            # If current hub is not the closest
            if closest_hub["Hub"] != hub["hub"]:
                mismatches.append({
                    "Pincode": pincode,
                    "Current Hub": hub["hub"],
                    "Current Distance (km)": next(d["Distance (km)"] for d in distances if d["Hub"] == hub["hub"]),
                    "Closest Hub": closest_hub["Hub"],
                    "Closest Distance (km)": closest_hub["Distance (km)"],
                    "Distance Difference (km)": round(next(d["Distance (km)"] for d in distances if d["Hub"] == hub["hub"]) - closest_hub["Distance (km)"], 2)
                })

if mismatches:
    mismatch_df = pd.DataFrame(mismatches).sort_values(by="Distance Difference (km)", ascending=False)
    st.subheader("Pincodes with potential better hub assignments")
    st.dataframe(mismatch_df)
    
    # Show details for each mismatch with route maps
    st.subheader("Detailed Mismatch Analysis with Route Maps")
    for idx, row in mismatch_df.iterrows():
        st.write(f"""
        **Pincode {row['Pincode']}** is currently assigned to **{row['Current Hub']}** ({row['Current Distance (km)']} km away)  
        but is actually closer to **{row['Closest Hub']}** ({row['Closest Distance (km)']} km away)  
        (Difference: {row['Distance Difference (km)']} km)
        """)
        
        # Get coordinates for current and closest hub
        current_hub = next(h for h in delivery_hubs if h["hub"] == row["Current Hub"])
        closest_hub = next(h for h in delivery_hubs if h["hub"] == row["Closest Hub"])
        pincode_coord = pincode_coords[row["Pincode"]]
        
        # Create a map comparing current vs. closest hub
        m = folium.Map(location=pincode_coord, zoom_start=12)
        
        # Add pincode marker
        folium.Marker(
            pincode_coord,
            popup=f"Pincode: {row['Pincode']}",
            icon=folium.Icon(color="blue", icon="map-pin")
        ).add_to(m)
        
        # Add current hub marker and route
        folium.Marker(
            [current_hub["lat"], current_hub["lon"]],
            popup=f"Current Hub: {current_hub['hub']}",
            icon=folium.Icon(color="red", icon="warehouse")
        ).add_to(m)
        
        folium.PolyLine(
            locations=[pincode_coord, [current_hub["lat"], current_hub["lon"]]],
            color="red",
            weight=2,
            opacity=0.7,
            tooltip=f"Current Route: {row['Current Distance (km)']} km"
        ).add_to(m)
        
        # Add closest hub marker and route
        folium.Marker(
            [closest_hub["lat"], closest_hub["lon"]],
            popup=f"Closest Hub: {closest_hub['hub']}",
            icon=folium.Icon(color="green", icon="warehouse")
        ).add_to(m)
        
        folium.PolyLine(
            locations=[pincode_coord, [closest_hub["lat"], closest_hub["lon"]]],
            color="green",
            weight=2,
            opacity=0.7,
            tooltip=f"Optimal Route: {row['Closest Distance (km)']} km"
        ).add_to(m)
        
        folium_static(m)
else:
    st.success("All pincodes are assigned to their geographically closest hub!")
